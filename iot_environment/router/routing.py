
"""Logical and real Linux routing for the IoT cyber range."""
import ipaddress
import json
import os
import re
import shutil
import subprocess
from threading import Lock
from config import NETWORKS
_route_lock = Lock()
_interface_pattern = re.compile(r"^[a-zA-Z0-9_.:-]{1,15}$")
# Logical route records. Docker creates connected routes for the
# networks attached to the router container.
_routes = [
    {
        "destination": name,
        "next_hop": "direct",
        "interface": None,
        "status": "CONNECTED",
        "subnet": settings.get("subnet"),
        "real_route_configured": False,
    }
    for name, settings in NETWORKS.items()
]
def _run_ip(args):
    """Execute a Linux ip command safely."""
    if shutil.which("ip") is None:
        raise RuntimeError(
            "'ip' command not found. Install iproute2 in the router image."
        )

    result = subprocess.run(
        ["ip", *args],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or "Linux networking command failed."
        )

    return result.stdout.strip()


def _validate_interface(interface):
    """Validate that an interface exists in this container."""
    if not isinstance(interface, str):
        raise ValueError("A Linux interface name is required.")

    if not _interface_pattern.fullmatch(interface):
        raise ValueError("Invalid interface name.")

    if not os.path.exists(f"/sys/class/net/{interface}"):
        raise ValueError(f"Interface '{interface}' does not exist.")


def _validate_cidr(cidr):
    """Validate and normalize an IP network."""
    try:
        return str(ipaddress.ip_network(cidr, strict=False))
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid destination subnet: {exc}") from exc


def get_routes():
    """Return a copy of the logical route table."""
    with _route_lock:
        return [route.copy() for route in _routes]


def find_route(destination):
    """Find a configured logical route by network name."""
    if not isinstance(destination, str):
        return None

    with _route_lock:
        for route in _routes:
            if route["destination"] == destination:
                return route.copy()

    return None


def get_system_routes():
    """Read the actual Linux IPv4 routing table."""
    output = _run_ip(["-j", "-4", "route", "show", "table", "all"])

    try:
        return json.loads(output or "[]")
    except json.JSONDecodeError as exc:
        raise RuntimeError("Could not parse Linux routes.") from exc


def get_ip_forwarding_status():
    """Check whether Linux IPv4 forwarding is enabled."""
    with open(
        "/proc/sys/net/ipv4/ip_forward", "r", encoding="utf-8"
    ) as file:
        enabled = file.read().strip() == "1"

    return {"ipv4_forwarding_enabled": enabled}


def enable_ip_forwarding():
    """Enable forwarding in this container's Linux network namespace."""
    result = subprocess.run(
        ["sysctl", "-w", "net.ipv4.ip_forward=1"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or
            "Could not enable IP forwarding; check container permissions."
        )

    return get_ip_forwarding_status()


def add_route(destination, next_hop="direct", interface=None):
    """Install a real Linux route for a configured network.

    For a directly attached network, Docker normally creates the route
    automatically. For a remote network, provide its gateway and interface.

    Example:
        add_route(
            "remote_network",
            next_hop="172.29.20.1",
            interface="eth1",
        )

    The destination's subnet must be configured in NETWORKS.
    """
    if not isinstance(destination, str) or destination not in NETWORKS:
        return False, "Destination network is not configured."

    subnet = NETWORKS[destination].get("subnet")

    if not subnet:
        return False, "Destination subnet is missing from config.py."

    try:
        network = ipaddress.ip_network(subnet, strict=False)

        if network.version != 4:
            return False, "This initial implementation supports IPv4 only."

        if not isinstance(next_hop, str) or not next_hop.strip():
            return False, "Next hop must be a non-empty string."

        # Do not reinstall a route for a directly connected Docker network.
        if next_hop == "direct":
            system_routes = get_system_routes()

            connected = any(
                route.get("dst") == str(network)
                and route.get("dev")
                for route in system_routes
            )

            if connected:
                return True, "Network is already directly connected."

            if interface is None:
                return False, (
                    "Network is not connected. Provide a real interface "
                    "before attempting route installation."
                )

            _validate_interface(interface)
            _run_ip(["route", "replace", str(network), "dev", interface])

        else:
            gateway = ipaddress.ip_address(next_hop.strip())

            if gateway.version != 4:
                return False, "Gateway must be an IPv4 address."

            if interface is None:
                return False, "Provide the outgoing Linux interface."

            _validate_interface(interface)

            _run_ip([
                "route", "replace", str(network),
                "via", str(gateway), "dev", interface,
            ])

        with _route_lock:
            existing = next(
                (
                    route for route in _routes
                    if route["destination"] == destination
                ),
                None,
            )

            record = {
                "destination": destination,
                "next_hop": next_hop,
                "interface": interface,
                "status": "ACTIVE",
                "subnet": str(network),
                "real_route_configured": True,
            }

            if existing:
                existing.update(record)
            else:
                _routes.append(record)

        return True, "Linux route configured successfully."

    except (ValueError, RuntimeError, OSError,
            subprocess.SubprocessError) as exc:
        return False, f"Route configuration failed: {exc}"


def remove_route(destination):
    """Remove a managed logical route and its real route if installed."""
    with _route_lock:
        route = next(
            (
                item for item in _routes
                if item["destination"] == destination
            ),
            None,
        )

        if route is None:
            return False, "Route not found."

        if route["real_route_configured"]:
            try:
                args = ["route", "del", route["subnet"]]

                if route["next_hop"] != "direct":
                    args.extend([
                        "via", route["next_hop"],
                        "dev", route["interface"],
                    ])
                elif route["interface"]:
                    args.extend(["dev", route["interface"]])

                _run_ip(args)

            except (RuntimeError, OSError,
                    subprocess.SubprocessError) as exc:
                return False, f"Could not remove Linux route: {exc}"

        _routes.remove(route)

    return True, "Route removed."

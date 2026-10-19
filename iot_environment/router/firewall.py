
"""Manage firewall rules inside the Linux router container."""

import ipaddress
import subprocess
from threading import Lock

_lock = Lock()
CHAIN = "IOT_RANGE"


def _run_iptables(*args):
    """Run iptables and return its output."""
    return subprocess.run(
        ["iptables", *args],
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
    )


def _validate_ip(address):
    """Accept a single IPv4 or IPv6 address, not a network range."""
    ip = ipaddress.ip_address(address)
    if ip.version != 4:
        raise ValueError("This initial firewall supports IPv4 only.")
    return str(ip)


def initialize_firewall():
    """Create a dedicated chain and attach it to FORWARD."""
    with _lock:
        result = _run_iptables("-n", "-L", CHAIN)

        # The chain already exists.
        if result.returncode == 0:
            pass


def setup_firewall():
    """Create the chain and hook it into forwarded traffic."""
    with _lock:
        chains = subprocess.run(
            ["iptables", "-S", CHAIN],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if chains.returncode != 0:
            _run_iptables("-N", CHAIN)

        rules = _run_iptables("-C", "FORWARD", "-j", CHAIN) \
            if _has_forward_hook() else None

        if rules is None:
            _run_iptables("-I", "FORWARD", "1", "-j", CHAIN)

        # Allow established traffic to continue; new traffic is evaluated
        # by the source-block rules below and the chain's final return.
        _ensure_rule(["-m", "conntrack", "--ctstate",
                      "ESTABLISHED,RELATED", "-j", "ACCEPT"])


def _has_forward_hook():
    result = subprocess.run(
        ["iptables", "-C", "FORWARD", "-j", CHAIN],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return result.returncode == 0


def _ensure_rule(args):
    exists = subprocess.run(
        ["iptables", "-C", CHAIN, *args],
        capture_output=True,
        text=True,
        timeout=5,
    )
    if exists.returncode != 0:
        _run_iptables("-A", CHAIN, *args)


def block_source(address):
    """Block forwarded IPv4 packets originating from one address."""
    address = _validate_ip(address)
    with _lock:
        setup_firewall()
        rule = ["-s", address, "-j", "DROP"]
        exists = subprocess.run(
            ["iptables", "-C", CHAIN, *rule],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if exists.returncode != 0:
            _run_iptables("-I", CHAIN, "1", *rule)
    return {"source_ip": address, "action": "BLOCKED"}


def unblock_source(address):
    """Remove the source-IP block managed by this module."""
    address = _validate_ip(address)
    with _lock:
        rule = ["-s", address, "-j", "DROP"]
        while True:
            result = subprocess.run(
                ["iptables", "-C", CHAIN, *rule],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                break
            _run_iptables("-D", CHAIN, *rule)
    return {"source_ip": address, "action": "UNBLOCKED"}


def get_firewall_rules():
    """Return rules in the dedicated chain."""
    result = _run_iptables("-S", CHAIN)
    return [line for line in result.stdout.splitlines()]

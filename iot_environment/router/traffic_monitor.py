
"""Read actual Linux network-interface traffic counters."""

from pathlib import Path


PROC_NET_DEV = Path("/proc/net/dev")


def get_interface_traffic():
    """Return byte, packet, error, and drop counters for each interface."""
    if not PROC_NET_DEV.exists():
        raise RuntimeError("/proc/net/dev is unavailable.")

    traffic = {}

    for line in PROC_NET_DEV.read_text().splitlines()[2:]:
        if ":" not in line:
            continue

        interface, values = line.split(":", 1)
        interface = interface.strip()
        counters = values.split()

        if len(counters) < 16:
            continue

        traffic[interface] = {
            "rx_bytes": int(counters[0]),
            "rx_packets": int(counters[1]),
            "rx_errors": int(counters[2]),
            "rx_drops": int(counters[3]),
            "tx_bytes": int(counters[8]),
            "tx_packets": int(counters[9]),
            "tx_errors": int(counters[10]),
            "tx_drops": int(counters[11]),
        }

    return traffic


def get_traffic_summary():
    """Return a summary of the interfaces visible inside this container."""
    interfaces = get_interface_traffic()

    return {
        "interface_count": len(interfaces),
        "interfaces": interfaces,
        "measurement": "cumulative Linux interface counters",
    }

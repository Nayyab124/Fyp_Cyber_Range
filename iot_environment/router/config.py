
"""
Central configuration for the IoT cyber-range router.

IMPORTANT FOR FUTURE EXTENSIONS:
- Add new network definitions here when the network topology changes.
- Do not add individual device IP addresses here as the device count grows.
- Use a device registry or Docker DNS for device discovery.
- Network definitions must match the networks configured in docker-compose.yml.

NOTE:
These are logical network names for the initial design.
They do not create real network interfaces or enable packet forwarding.
"""

# Router service configuration
ROUTER_NAME = "IoT Gateway"
ROUTER_HOST = "0.0.0.0"
ROUTER_PORT = 5000

# Initial logical networks.
# Update these if you later introduce separate sensor, actuator,
# management, or attacker networks in docker-compose.yml.
NETWORKS = {
    "iot_network": {
        "description": "Network for IoT devices and MQTT communication",
        "subnet": "172.29.10.0/24",
        "router_ip": "172.29.10.2",
    },
    "attacker_network": {
        "description": "Isolated network for the attacker service",
        "subnet": "172.29.20.0/24",
        "router_ip": "172.29.20.2",
    },
}

# Initial MQTT settings.
# Keep MQTT authentication and topic authorization in the broker configuration;
# the router's network firewall is a separate security layer.
MQTT_PORT = 1883
MQTT_PROTOCOL = "tcp"

# Keep the router's control API available to the cyber-range components.
# Do not expose it publicly when deploying the range.
API_ENABLED = True

# Maximum number of recent events retained in memory.
# Persistent storage can be added later if experiment history must survive restarts.
MAX_SECURITY_EVENTS = 500


"""Main API for the IoT cyber-range router."""

from flask import Flask, jsonify, request

from config import ROUTER_HOST, ROUTER_PORT, ROUTER_NAME
from firewall import (
    setup_firewall,
    block_source,
    unblock_source,
    get_firewall_rules,
)
from routing import get_routes, get_system_routes, get_ip_forwarding_status
from traffic_monitor import get_traffic_summary
from security_logger import log_event, get_recent_events


app = Flask(__name__)

router_state = {
    "service": ROUTER_NAME,
    "status": "STARTING",
    "firewall_initialized": False,
}


def initialize_router():
    """Initialize the real Linux firewall."""
    try:
        setup_firewall()
        router_state["firewall_initialized"] = True
        router_state["status"] = "ONLINE"

        log_event(
            "FIREWALL_INITIALIZED",
            {"message": "Router firewall initialized successfully."},
        )
    except Exception as exc:
        router_state["firewall_initialized"] = False
        router_state["status"] = "DEGRADED"

        log_event(
            "FIREWALL_INITIALIZATION_FAILED",
            {"error": str(exc)},
            severity="CRITICAL",
        )


@app.get("/")
def home():
    return jsonify({
        "service": ROUTER_NAME,
        "status": router_state["status"],
        "endpoints": [
            "/health",
            "/state",
            "/routes",
            "/traffic/interfaces",
            "/firewall/rules",
            "/events",
        ],
    })


@app.get("/health")
def health():
    code = 200 if router_state["status"] == "ONLINE" else 503
    return jsonify(router_state), code


@app.get("/state")
def state():
    return jsonify(router_state)


@app.get("/routes")
def routes():
    # These are the routes currently exposed by routing.py.
    # They are logical routes, not proof of OS packet forwarding.
    return jsonify({"routes": get_routes()})


@app.get("/traffic/interfaces")
def interface_traffic():
    try:
        return jsonify(get_traffic_summary())
    except (OSError, RuntimeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 500


@app.get("/firewall/rules")
def firewall_rules():
    try:
        return jsonify({"rules": get_firewall_rules()})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.post("/firewall/block")
def firewall_block():
    data = request.get_json(silent=True) or {}
    source_ip = data.get("source_ip")

    if not isinstance(source_ip, str) or not source_ip.strip():
        return jsonify({
            "error": "Provide source_ip in the JSON request body."
        }), 400

    try:
        result = block_source(source_ip)
        log_event(
            "TRAFFIC_BLOCK_RULE_ADDED",
            result,
            severity="WARNING",
        )
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        log_event(
            "FIREWALL_OPERATION_FAILED",
            {"operation": "block", "error": str(exc)},
            severity="CRITICAL",
        )
        return jsonify({"error": "Firewall operation failed."}), 500


@app.post("/firewall/unblock")
def firewall_unblock():
    data = request.get_json(silent=True) or {}
    source_ip = data.get("source_ip")

    if not isinstance(source_ip, str) or not source_ip.strip():
        return jsonify({
            "error": "Provide source_ip in the JSON request body."
        }), 400

    try:
        result = unblock_source(source_ip)
        log_event("TRAFFIC_BLOCK_RULE_REMOVED", result)
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        log_event(
            "FIREWALL_OPERATION_FAILED",
            {"operation": "unblock", "error": str(exc)},
            severity="CRITICAL",
        )
        return jsonify({"error": "Firewall operation failed."}), 500


@app.get("/events")
def events():
    limit = request.args.get("limit", default=100, type=int)
    return jsonify({"events": get_recent_events(limit)})


if __name__ == "__main__":
    initialize_router()
    app.run(host=ROUTER_HOST, port=ROUTER_PORT)

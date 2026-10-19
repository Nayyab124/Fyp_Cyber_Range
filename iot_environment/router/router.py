from flask import Flask, jsonify

app = Flask(__name__)

router_state = {
    "status": "ONLINE",
    "attacker_blocked": False,
    "failed_attempts": 0,
    "successful_logins": 0
}


@app.route("/")
def home():
    return jsonify({
        "service": "IoT Router",
        "status": router_state["status"]
    })


@app.route("/health")
def health():
    return jsonify({
        "service": "router",
        "status": router_state["status"]
    })


@app.route("/state")
def state():
    return jsonify(router_state)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
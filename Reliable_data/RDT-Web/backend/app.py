# backend/app.py

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from rdt import simulate_stop_and_wait

ROOT = os.path.dirname(os.path.abspath(__file__))
FRONTEND = os.path.normpath(os.path.join(ROOT, "..", "frontend"))

app = Flask(__name__, static_folder=FRONTEND, static_url_path="")
CORS(app)  # Allow frontend (different origin) to call the API


@app.route("/api/simulate", methods=["POST"])
def simulate():
    """
    HTTP endpoint to run a Stop-and-Wait simulation.
    Expects JSON:
      {
        "message": "Hello world",
        "packet_size": 4,
        "loss_rate": 0.1,
        "corruption_rate": 0.1,
        "ack_loss_rate": 0.05,
        "max_retries_per_packet": 20
      }
    """
    data = request.get_json(force=True)

    message = data.get("message", "")
    packet_size = int(data.get("packet_size", 4))
    loss_rate = float(data.get("loss_rate", 0.1))
    corruption_rate = float(data.get("corruption_rate", 0.1))
    ack_loss_rate = float(data.get("ack_loss_rate", 0.05))
    max_retries_per_packet = int(data.get("max_retries_per_packet", 20))

    result = simulate_stop_and_wait(
        message=message,
        packet_size=packet_size,
        loss_rate=loss_rate,
        corruption_rate=corruption_rate,
        ack_loss_rate=ack_loss_rate,
        max_retries_per_packet=max_retries_per_packet,
    )

    return jsonify(result)


@app.route("/")
def index():
    # serve the frontend index.html
    return send_from_directory(FRONTEND, "index.html")


@app.route('/<path:path>')
def static_proxy(path):
    # serve other frontend static files (js/css)
    return send_from_directory(FRONTEND, path)


if __name__ == "__main__":
    # Run backend API server
    app.run(host="127.0.0.1", port=5000, debug=True)

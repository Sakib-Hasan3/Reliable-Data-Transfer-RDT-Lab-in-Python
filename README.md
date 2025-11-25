
# RDT-Web — Reliable Data Transfer Simulator

Project Title: RDT-Web — Reliable Data Transfer Simulator

Description: A small educational web app that simulates Stop-and-Wait reliable data transfer over an unreliable channel. The backend is a Flask API that runs simulations (packet loss, corruption, ACK loss) and the frontend is a static HTML/JS UI that visualizes events and results. This is useful for networking students and educators who want to explore how reliability protocols behave under failures.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

Prerequisites:
- Python 3.8+ (3.11 recommended)
- Git (optional, to clone)

1. Clone the repo
```bash
git clone https://github.com/yourusername/projectname.git
cd projectname
```

2. (Optional) Create and activate a virtual environment (Windows PowerShell):
```powershell
python -m venv .\RDT-Web\venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\RDT-Web\venv\Scripts\Activate.ps1
```

3. Install Python dependencies
```powershell
pip install -r .\RDT-Web\requirements.txt
```

Note: This project uses a simple static frontend (no npm required). If you decide to extend the frontend and add a build step, add instructions here.

## Usage

Run the backend (from project root):
```powershell
python .\RDT-Web\backend\app.py
```

Or change directory to the backend and run:
```powershell
Set-Location .\RDT-Web\backend
python .\app.py
```

The backend serves the static frontend from `RDT-Web/frontend` and exposes an API endpoint at `http://127.0.0.1:5000/api/simulate`.

Open `RDT-Web/frontend/index.html` in your browser (or visit `http://127.0.0.1:5000/` after starting the backend) to view the UI.

Example usage via `curl` (run after starting server):
```bash
curl -X POST http://127.0.0.1:5000/api/simulate \
	-H "Content-Type: application/json" \
	-d '{"message":"Hello world","packet_size":4,"loss_rate":0.1,"corruption_rate":0.1,"ack_loss_rate":0.05,"max_retries_per_packet":20}'
```

## Features
Feature 1: Stop-and-Wait simulation with configurable packet/ACK loss and corruption.
Feature 2: Event timeline describing each send/receive/loss/corruption/ACK event.
Feature 3: Reconstructed receiver data and statistics (packets sent, retransmissions, losses).

## API Documentation
POST /api/simulate
- Description: Run a Stop-and-Wait simulation with the given parameters.
- Request JSON fields:
	- `message` (string): the payload to send.
	- `packet_size` (int): size of each packet (default 4).
	- `loss_rate` (float): probability a data packet is lost (0.0–1.0).
	- `corruption_rate` (float): probability a data packet is corrupted (0.0–1.0).
	- `ack_loss_rate` (float): probability an ACK is lost (0.0–1.0).
	- `max_retries_per_packet` (int): abort after this many retries per packet.

Example request (JSON):
```json
{
	"message": "Hello world",
	"packet_size": 4,
	"loss_rate": 0.1,
	"corruption_rate": 0.1,
	"ack_loss_rate": 0.05,
	"max_retries_per_packet": 20
}
```

Example response (truncated):
```json
{
	"events": [
		{"step": 1, "type": "send_packet", "who": "sender", "seq": 0, "data": "Hell", ...},
		{"step": 2, "type": "packet_received", "who": "receiver", "seq": 0, "data": "Hell", ...},
		...
	],
	"final_data": "Hello world",
	"stats": {"total_packets": 3, "packets_sent": 4, "retransmissions": 1, ...},
	"config_used": {"packet_size": 4, "loss_rate": 0.1, ...}
}
```

## Contributing
Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) if you plan to open pull requests or issues.

General workflow:
- Fork the repo
- Create a feature branch
- Run the app and add tests if applicable
- Open a pull request with a clear description

## License
This project is licensed under the MIT License — see the `LICENSE` file for details.

## Contact
Maintainer: [Mohammed Sakib Hasan](https://github.com/yourusername)

You can also open issues on the repo for bugs or feature requests.

---

If you'd like, I can also add a small `run-backend.ps1` script to make launching the server easier on Windows.

## Project Structure

```bash
RDT-Web/
├── backend/
│   ├── app.py
│   └── rdt/
│       ├── __init__.py
│       ├── packet.py
│       ├── unreliable_channel.py
│       └── stop_and_wait.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── requirements.txt
└── README.md

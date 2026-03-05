from flask import Flask, render_template, request, jsonify
import time

app = Flask(__name__)

# Store workstation info in memory
workstations_data = {}

# -----------------------------
# API: Receive data from PowerShell
# -----------------------------
@app.route("/update", methods=["POST"])
def update_workstation():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    ws_name = data.get("system")

    if ws_name:

        status_text = str(data.get("status", "Unknown"))

        ram_usage = round(data.get("ramUsedPercent", 0), 2)
        cpu_usage = round(data.get("cpuLoadPercent", 0), 2)

        disk_info = data.get("disk", [])
        top_processes = data.get("topProcesses", [])

        color = "green" if status_text.lower() == "working" else "red"

        # Save workstation info
        workstations_data[ws_name] = {
            "ram": ram_usage,
            "cpu": cpu_usage,
            "disk": disk_info,
            "topProcesses": top_processes,
            "status": status_text,
            "color": color,
            "last_seen": time.time()
        }

        print(f"Received data from {ws_name}")

        return jsonify({"message": "Data updated"}), 200

    return jsonify({"error": "Invalid data"}), 400


# -----------------------------
# Dashboard
# -----------------------------
@app.route("/")
def dashboard():

    display_data = []

    current_time = time.time()

    for ws_name, info in workstations_data.items():

        last_seen = info.get("last_seen", 0)

        # If no update for 120 seconds → Offline
        if current_time - last_seen > 120:
            status = "Offline"
            color = "red"
        else:
            status = "Online"
            color = "green"

        display_data.append({
            "name": ws_name,
            "ram": info.get("ram", 0),
            "cpu": info.get("cpu", 0),
            "disk": info.get("disk", []),
            "topProcesses": info.get("topProcesses", []),
            "status": status,
            "color": color
        })

    return render_template("index.j2", workstations=display_data)


# -----------------------------
# Run Flask Server
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
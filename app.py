from flask import Flask, request, jsonify
import csv
import os
import random
from twilio.rest import Client

# --------------------------------------------------------------------
# TWILIO CONFIG (real credentials)
# --------------------------------------------------------------------
ACCOUNT_SID = "******************************"
AUTH_TOKEN  = "******************************"
FROM_NUMBER = "*************0"
TO_NUMBER   = "***************0"

twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# CSV log file
CSV_FILE = "mmb_log.csv"

# If file doesn't exist, create it and write header
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["temp", "acc_x", "acc_y", "acc_z", "mic"])

# --------------------------------------------------------------------
app = Flask(__name__)

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    print(f"[+] Received from ESP32 → {data}")

    # ----- append to csv -----
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            [data.get("temp"), data.get("acc_x"), data.get("acc_y"),
             data.get("acc_z"), data.get("mic")]
        )

    # ----- random irregularity (10% chance) -----
    if random.random() < 0.10:
        msg = f"⚠️  MMB ALERT : Irregular pattern detected! Data = {data}"
        twilio_client.messages.create(
            body=msg,
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )
        return jsonify({"status": "irregular", "sms_sent": True})

    return jsonify({"status": "normal", "sms_sent": False})

# --------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

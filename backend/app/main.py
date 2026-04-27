from fastapi import FastAPI
import socket
import json
from datetime import datetime

app = FastAPI()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("logstash", 5000))

def send_log(level, message):
    log = {
        "@timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "service": "backend",
        "message": message
    }
    sock.sendall((json.dumps(log)+"\n").encode())

@app.get("/")
def home():
    send_log("INFO", "home endpoint called")
    return {"message": "AI DevOps Monitoring ??"}

@app.get("/error")
def error():
    send_log("ERROR", "error simulated")
    return {"error": "something failed"}

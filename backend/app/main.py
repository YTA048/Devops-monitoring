from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
import time, requests

app = FastAPI()
security = HTTPBasic()

# CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AUTH
def auth(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "admin" or credentials.password != "admin":
        raise HTTPException(status_code=401)
    return credentials.username

# MONITOR
@app.get("/monitor")
def monitor(user: str = Depends(auth)):

    services = [
        {"url": "https://google.com"},
        {"url": "https://github.com"},
        {"url": "https://aws.amazon.com"}
    ]

    results = []
    alerts = []
    recommendations = []

    for s in services:
        start = time.time()
        try:
            r = requests.get(s["url"], timeout=2)
            latency = round(time.time() - start, 2)

            status = "UP" if r.status_code == 200 else "DOWN"

            if latency > 1:
                alerts.append(f"?? Slow: {s['url']}")

            results.append({
                "url": s["url"],
                "latency": latency,
                "status": status
            })

        except:
            alerts.append(f"?? DOWN: {s['url']}")
            results.append({
                "url": s["url"],
                "latency": None,
                "status": "DOWN"
            })

    score = 100 - (len(alerts) * 10)

    return {
        "services": results,
        "alerts": alerts,
        "recommendations": ["scale servers", "check latency"],
        "ai_score": score,
        "timestamp": time.time()
    }

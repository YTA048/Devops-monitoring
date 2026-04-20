import requests
from ..database.db import connect_db

def check_service(url):
    try:
        response = requests.get(url, timeout=5)
        status = "UP" if response.status_code == 200 else "DOWN"
        code = response.status_code
    except requests.exceptions.RequestException as e:
        print(f"ALERT! {url} is DOWN: {e}")
        status = "DOWN"
        code = None

    # Save to database
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO checks (url, status, code) VALUES (?, ?, ?)", (url, status, code))
    conn.commit()
    conn.close()

    return {
        "url": url,
        "status": status,
        "code": code
    }
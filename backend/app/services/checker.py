import requests

def check_service(url):
    try:
        response = requests.get(url)
        return {
            "url": url,
            "status": "UP",
            "code": response.status_code
        }
    except:
        return {
            "url": url,
            "status": "DOWN"
        }
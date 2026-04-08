from fastapi import APIRouter
from backend.app.services.checker import check_service
from backend.app.database.db import connect_db

router = APIRouter()

# 🔥 check أي URL
@router.get("/check")
def check(url: str):
    return check_service(url)
@router.get("/history")
def get_history():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM checks")
    rows = cursor.fetchall()

    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "url": row[1],
            "status": row[2],
            "code": row[3]
        })

    return result
@router.delete("/delete")
def delete_all():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM checks")

    conn.commit()
    conn.close()

    return {"message": "All data deleted"}
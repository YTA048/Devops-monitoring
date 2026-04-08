from fastapi import FastAPI
from backend.app.routes.services import router

app = FastAPI()

app.include_router(router)

@app.get("/")
def home():
    return {"message": "DevOps Monitoring is running"}

from backend.app.database.db import create_table

create_table()
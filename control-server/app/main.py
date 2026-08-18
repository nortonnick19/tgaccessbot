from fastapi import FastAPI
from database import init_db


app = FastAPI(
    title="TG Access Control API",
    version="0.1"
)


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "control-server"
    }

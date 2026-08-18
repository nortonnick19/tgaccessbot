from fastapi import FastAPI

from database import init_db
from api.access import router as access_router


app = FastAPI(
    title="TG Access Control API",
    version="0.2"
)


app.include_router(
    access_router
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

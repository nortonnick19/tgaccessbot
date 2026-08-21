from fastapi import FastAPI

from database import init_db

from api.access import router as access_router
from api.relay import router as relay_router



app = FastAPI(
    title="TG Access Control API",
    version="0.3"
)



# ==========================
# Routers
# ==========================

app.include_router(
    access_router
)


app.include_router(
    relay_router
)



# ==========================
# Startup
# ==========================

@app.on_event("startup")
async def startup():

    await init_db()



# ==========================
# Health check
# ==========================

@app.get("/")
async def root():

    return {

        "status": "online",

        "service": "control-server"

    }

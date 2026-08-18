from fastapi import FastAPI


app = FastAPI(
    title="TG Access Control API",
    version="0.1"
)


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "control-server"
    }

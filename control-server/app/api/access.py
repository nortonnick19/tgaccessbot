from datetime import datetime

from fastapi import (
    APIRouter,
    Header,
    HTTPException
)

from sqlalchemy import select

from database import async_session
from models import (
    Server,
    AccessRequest
)

from config import AGENT_SECRET

from services.telegram import send_access_request


router = APIRouter(
    prefix="/api/v1/access",
    tags=["access"]
)


@router.post("/event")
async def access_event(
    data: dict,
    x_agent_key: str = Header(None)
):

    # Проверка ключа агента
    if x_agent_key != AGENT_SECRET:

        raise HTTPException(
            status_code=403,
            detail="Invalid agent key"
        )


    required_fields = [
        "server_id",
        "username",
        "source_ip",
        "event_type"
    ]


    for field in required_fields:

        if field not in data:

            raise HTTPException(
                status_code=400,
                detail=f"Missing field: {field}"
            )


    async with async_session() as session:


        # Ищем сервер

        result = await session.execute(
            select(Server).where(
                Server.id == data["server_id"]
            )
        )


        server = result.scalar_one_or_none()


        if not server:

            raise HTTPException(
                status_code=404,
                detail="Server not found"
            )


        # Создаем запрос доступа

        request = AccessRequest(

            server_id=server.id,

            username=data["username"],

            source_ip=data["source_ip"],

            event_type=data["event_type"],

            reason=data.get(
                "reason",
                "Unknown"
            ),

            status="WAITING",

            created_at=datetime.utcnow()

        )


        session.add(request)

        await session.commit()

        await session.refresh(request)



    # Отправка уведомления в Telegram

    await send_access_request(

        server_name=server.name,

        username=request.username,

        source_ip=request.source_ip,

        event_type=request.event_type,

        reason=request.reason,

        request_id=request.id

    )


    return {

        "status": "received",

        "request_id": request.id

    }

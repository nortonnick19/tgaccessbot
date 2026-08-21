import logging

from fastapi import (
    APIRouter,
    Header,
    HTTPException
)

from pydantic import BaseModel

from database import async_session

from models import (
    AccessRequest,
    Server
)

from sqlalchemy import select

from config import AGENT_SECRET


logger = logging.getLogger(
    "access-api"
)


router = APIRouter(
    prefix="/api/v1/access"
)



class AccessEvent(BaseModel):

    server_id: int

    username: str = "unknown"

    source_ip: str

    country: str = "Unknown"

    event_type: str

    reason: str | None = None



@router.post("/event")
async def access_event(

    event: AccessEvent,

    x_agent_key: str = Header(None)

):


    if x_agent_key != AGENT_SECRET:

        raise HTTPException(
            status_code=403,
            detail="Invalid key"
        )



    async with async_session() as session:


        result = await session.execute(

            select(Server)
            .where(
                Server.id == event.server_id
            )

        )


        server = result.scalar_one_or_none()



        if not server:

            raise HTTPException(
                status_code=404,
                detail="Server not found"
            )



        request = AccessRequest(

            server_id=event.server_id,

            username=event.username,

            source_ip=event.source_ip,

            country=event.country,

            event_type=event.event_type,

            reason=event.reason,

            status="WAITING"

        )


        session.add(request)

        await session.commit()

        await session.refresh(request)



        logger.info(
            "New access request %s from %s",
            request.id,
            request.source_ip
        )


    return {

        "status":"received",

        "request_id":request.id

    }

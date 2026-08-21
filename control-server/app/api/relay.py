import logging

from fastapi import (
    APIRouter,
    Header,
    HTTPException
)

from sqlalchemy import select

from database import async_session
from models import Server
from config import AGENT_SECRET


logger = logging.getLogger(
    "relay-api"
)


router = APIRouter(
    prefix="/api/v1/relay",
    tags=["relay"]
)



@router.get("/servers")
async def get_servers(
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
                Server.active == True
            )

        )


        servers = result.scalars().all()



        data = []


        for server in servers:

            data.append({

                "id": server.id,

                "name": server.name,

                "public_ip": server.public_ip,

                "rdp_port": server.rdp_port,

                "ipset_name": server.ipset_name

            })



        logger.info(
            "Relay requested server list: %s servers",
            len(data)
        )


        return data

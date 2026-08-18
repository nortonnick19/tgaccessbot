import sys
import asyncio
import logging
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))


from sqlalchemy import select

from database import async_session
from models import Whitelist, Server
from services.firewall import add_ip_to_firewall


logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger("sync_firewall")


async def sync_firewall():

    logger.info("Starting firewall sync")

    synced = 0


    async with async_session() as session:

        result = await session.execute(
            select(
                Whitelist,
                Server
            )
            .join(
                Server,
                Server.id == Whitelist.server_id
            )
            .where(
                Server.active == True,
                Whitelist.permanent == True
            )
        )


        rows = result.all()


        for whitelist, server in rows:

            success = await add_ip_to_firewall(
                server.id,
                whitelist.ip
            )


            if success:

                synced += 1

                logger.info(
                    f"Synced {whitelist.ip} -> {server.name}"
                )

            else:

                logger.error(
                    f"Failed {whitelist.ip}"
                )


    logger.info(
        f"Firewall sync completed: {synced} IPs"
    )



if __name__ == "__main__":

    asyncio.run(
        sync_firewall()
    )

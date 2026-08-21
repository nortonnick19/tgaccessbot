import asyncio
import logging
import subprocess

from datetime import datetime

from sqlalchemy import select

from database import async_session
from models import Whitelist


logger = logging.getLogger(
    "whitelist-cleaner"
)


def remove_ip_from_ipset(
    ipset_name,
    ip
):

    try:

        subprocess.run(
            [
                "ipset",
                "del",
                ipset_name,
                ip
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


        logger.info(
            "Removed %s from %s",
            ip,
            ipset_name
        )


    except Exception as e:

        logger.error(
            "ipset delete error: %s",
            e
        )



async def whitelist_cleanup_worker():


    logger.info(
        "Whitelist cleanup started"
    )


    while True:


        try:


            async with async_session() as session:


                result = await session.execute(

                    select(Whitelist)
                    .where(
                        Whitelist.expires_at <= datetime.utcnow()
                    )

                )


                expired = result.scalars().all()



                for item in expired:


                    if item.server.ipset_name:

                        remove_ip_from_ipset(

                            item.server.ipset_name,

                            item.ip

                        )


                    await session.delete(
                        item
                    )



                await session.commit()



        except Exception as e:

            logger.exception(
                "Cleanup error: %s",
                e
            )


        await asyncio.sleep(
            3600
        )

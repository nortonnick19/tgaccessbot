import asyncio
import logging

from datetime import datetime

from aiogram import (
    Bot,
    Dispatcher
)

from aiogram.client.default import (
    DefaultBotProperties
)

from aiogram.enums import (
    ParseMode
)

from aiogram.filters import Command

from aiogram.types import Message


from sqlalchemy import (
    select
)


from config import BOT_TOKEN

from database import async_session


from models import (
    User,
    AccessRequest,
    Server
)


from handlers.access import (
    router as access_router
)


from handlers.servers import (
    router as servers_router
)


from services.telegram import (
    send_access_request
)



# ==================================================
# LOGGING
# ==================================================

logging.basicConfig(

    level=logging.INFO,

    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    )

)


logger = logging.getLogger(
    "tgaccess-bot"
)




# ==================================================
# BOT
# ==================================================

bot = Bot(

    token=BOT_TOKEN,

    default=DefaultBotProperties(

        parse_mode=ParseMode.HTML

    )

)


dp = Dispatcher()



# ==================================================
# ROUTERS
# ==================================================

dp.include_router(
    access_router
)


dp.include_router(
    servers_router
)





# ==================================================
# ADMIN CHECK
# ==================================================

async def is_admin(
    telegram_id: int
):

    async with async_session() as session:


        result = await session.execute(

            select(User)

            .where(

                User.telegram_id ==
                str(telegram_id),

                User.active == True,

                User.role == "ADMIN"

            )

        )


        user = (
            result
            .scalar_one_or_none()
        )


        return user is not None






# ==================================================
# SEND TO ADMINS
# ==================================================

async def get_admin_ids():


    async with async_session() as session:


        result = await session.execute(

            select(User.telegram_id)

            .where(

                User.active == True,

                User.role == "ADMIN"

            )

        )


        return [

            int(x)

            for x in result.scalars().all()

        ]






# ==================================================
# NOTIFICATION WORKER
# ==================================================

async def notification_worker():


    logger.info(
        "Notification worker started"
    )


    while True:


        try:


            async with async_session() as session:



                result = await session.execute(

                    select(
                        AccessRequest
                    )

                    .where(

                        AccessRequest.status == "WAITING",

                        AccessRequest.notified_at == None

                    )

                    .order_by(
                        AccessRequest.id.asc()
                    )

                    .limit(20)

                )



                requests = (
                    result
                    .scalars()
                    .all()
                )



                if requests:


                    admins = await get_admin_ids()



                    for request in requests:



                        server_result = await session.execute(

                            select(Server)

                            .where(

                                Server.id ==
                                request.server_id

                            )

                        )



                        server = (

                            server_result
                            .scalar_one_or_none()

                        )



                        if not server:


                            continue





                        message_ids = []



                        for admin_id in admins:


                            try:


                                msg = await send_access_request(

                                    bot=bot,

                                    chat_id=admin_id,

                                    request_id=request.id,

                                    server_name=server.name,

                                    source_ip=request.source_ip,

                                    country=request.country or "Unknown"

                                )


                                if msg:

                                    message_ids.append(
                                        msg.message_id
                                    )



                            except Exception as e:


                                logger.error(

                                    "Telegram send error %s: %s",

                                    admin_id,

                                    e

                                )





                        if message_ids:


                            request.telegram_message_id = (
                                message_ids[0]
                            )


                            request.notified_at = (
                                datetime.utcnow()
                            )


                            await session.commit()



                            logger.info(

                                "Notification sent for request %s",

                                request.id

                            )




        except Exception as e:


            logger.exception(

                "Notification worker error: %s",

                e

            )




        await asyncio.sleep(
            5
        )






# ==================================================
# COMMANDS
# ==================================================

@dp.message(
    Command("start")
)

async def start_handler(
    message: Message
):


    if not await is_admin(
        message.from_user.id
    ):


        await message.answer(

            "⛔ Access denied"

        )

        return



    await message.answer(

        "🛡 <b>TG Access Control</b>\n\n"
        "🟢 System online"

    )







@dp.message(
    Command("status")
)

async def status_handler(
    message: Message
):


    if not await is_admin(

        message.from_user.id

    ):

        return



    await message.answer(

        "🟢 Bot online"

    )







# ==================================================
# STARTUP
# ==================================================

async def main():


    logger.info(

        "Starting TG Access Control Bot"

    )



    worker = asyncio.create_task(

        notification_worker()

    )



    try:


        await dp.start_polling(
            bot
        )


    finally:


        worker.cancel()


        await bot.session.close()





if __name__ == "__main__":


    asyncio.run(
        main()
    )

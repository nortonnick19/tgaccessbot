import asyncio
import logging

from aiogram import (
    Bot,
    Dispatcher,
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from sqlalchemy import select

from config import BOT_TOKEN

from database import async_session

from models import User

from handlers.servers import router as servers_router
from handlers.access import router as access_router


# ==========================
# Logging
# ==========================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    )
)


logger = logging.getLogger(
    "tgaccess"
)


# ==========================
# Bot
# ==========================

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)


dp = Dispatcher()


# ==========================
# Routers
# ==========================

dp.include_router(
    servers_router
)

dp.include_router(
    access_router
)


# ==========================
# Auth
# ==========================

async def is_admin(
    telegram_id: int
):

    async with async_session() as session:

        result = await session.execute(
            select(User)
            .where(
                User.telegram_id == str(telegram_id),
                User.active == True,
                User.role == "ADMIN"
            )
        )

        user = result.scalar_one_or_none()


        return user is not None



# ==========================
# Commands
# ==========================

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
        "🟢 System online\n\n"
        "Доступ разрешен"
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



# ==========================
# Startup
# ==========================

async def main():

    logger.info(
        "Starting TG Access Control Bot"
    )


    await dp.start_polling(
        bot
    )



if __name__ == "__main__":

    asyncio.run(
        main()
    )

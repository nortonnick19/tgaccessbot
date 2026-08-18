import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN

from middleware.auth import AdminMiddleware

from handlers.servers import router as servers_router


# ==========================
# Logging
# ==========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
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


# ==========================
# Dispatcher
# ==========================

dp = Dispatcher()


# ==========================
# Middleware
# ==========================

dp.message.middleware(
    AdminMiddleware()
)


# ==========================
# Routers
# ==========================

dp.include_router(
    servers_router
)


# ==========================
# Commands
# ==========================

from aiogram.filters import Command
from aiogram.types import Message


@dp.message(Command("start"))
async def start_handler(
    message: Message
):

    await message.answer(
        "🛡 <b>TG Access Control</b>\n\n"
        "🟢 System online\n\n"
        "Доступ разрешен"
    )


# ==========================
# Startup
# ==========================

async def main():

    logging.info(
        "Starting TG Access Control Bot"
    )

    await dp.start_polling(
        bot
    )


if __name__ == "__main__":

    asyncio.run(main())

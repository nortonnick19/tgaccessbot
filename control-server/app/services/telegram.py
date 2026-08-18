import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, ADMIN_IDS


logger = logging.getLogger(__name__)


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)


def access_keyboard(request_id: int):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ APPROVE",
                    callback_data=f"approve:{request_id}"
                ),
                InlineKeyboardButton(
                    text="⛔ BLOCK",
                    callback_data=f"block:{request_id}"
                )
            ]
        ]
    )


async def send_access_request(
    server_name: str,
    username: str,
    source_ip: str,
    event_type: str,
    reason: str,
    request_id: int
):

    text = (
        "🚨 <b>New Access Request</b>\n\n"
        f"🖥 Server: <b>{server_name}</b>\n"
        f"👤 User: <b>{username}</b>\n"
        f"🌐 IP: <b>{source_ip}</b>\n\n"
        f"⚠️ Event: <b>{event_type}</b>\n"
        f"📌 Reason: <b>{reason}</b>\n\n"
        f"ID: {request_id}"
    )


    keyboard = access_keyboard(
        request_id
    )


    for admin_id in ADMIN_IDS:

        try:

            await bot.send_message(
                chat_id=admin_id,
                text=text,
                reply_markup=keyboard
            )

        except Exception as e:

            logger.error(
                f"Telegram send error: {e}"
            )

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from sqlalchemy import select

from database import async_session
from models import Server


router = Router()


# ==========================
# /servers
# ==========================

@router.message(Command("servers"))
async def servers_handler(
    message: Message
):

    async with async_session() as session:

        result = await session.execute(
            select(Server)
            .order_by(Server.id)
        )

        servers = result.scalars().all()


    if not servers:

        await message.answer(
            "❌ Серверы отсутствуют"
        )

        return


    text = (
        "🖥 <b>Servers</b>\n\n"
    )


    for server in servers:

        status = (
            "🟢"
            if server.active
            else
            "🔴"
        )


        text += (
            f"{status} <b>{server.name}</b>\n"
            f"🌐 {server.domain}\n"
            f"IP: <code>{server.ip}</code>\n"
            f"ID: {server.id}\n\n"
        )


    await message.answer(
        text
    )

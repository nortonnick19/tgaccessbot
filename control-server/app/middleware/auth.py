from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from sqlalchemy import select

from database import async_session
from models import User


class AdminMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler,
        event: TelegramObject,
        data: dict
    ):

        user = data.get("event_from_user")

        if not user:
            return


        async with async_session() as session:

            result = await session.execute(
                select(User).where(
                    User.telegram_id == str(user.id),
                    User.active == True,
                    User.role == "ADMIN"
                )
            )

            admin = result.scalar_one_or_none()


        if not admin:

            await user.send_message(
                "⛔ Доступ запрещен"
            )

            return


        return await handler(
            event,
            data
        )

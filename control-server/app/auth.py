from sqlalchemy import select

from database import async_session
from models import User


async def is_admin(telegram_id: int):

    async with async_session() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == str(telegram_id),
                User.active == True,
                User.role == "ADMIN"
            )
        )

        user = result.scalar_one_or_none()

        return user is not None

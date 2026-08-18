import asyncio

from database import async_session
from models import User


ADMIN_ID = "5343045600"
USERNAME = "S19NICK"


async def main():

    async with async_session() as session:

        user = User(
            telegram_id=ADMIN_ID,
            username=USERNAME,
            role="ADMIN",
            active=True
        )

        session.add(user)

        await session.commit()


asyncio.run(main())

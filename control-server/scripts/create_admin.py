import asyncio
import os
import sys
from datetime import datetime


sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../app"
        )
    )
)


from sqlalchemy import select

from database import async_session
from models import User



TELEGRAM_ID = "5343045600"

USERNAME = "S19NICK"

FULL_NAME = "Administrator"



async def create_admin():


    async with async_session() as session:


        result = await session.execute(
            select(User).where(
                User.telegram_id == TELEGRAM_ID
            )
        )


        user = result.scalar_one_or_none()



        if user:


            user.username = USERNAME
            user.full_name = FULL_NAME
            user.role = "ADMIN"
            user.active = True


            print(
                "Admin updated"
            )


        else:


            user = User(

                telegram_id=TELEGRAM_ID,

                username=USERNAME,

                full_name=FULL_NAME,

                role="ADMIN",

                active=True,

                created_at=datetime.utcnow()

            )


            session.add(user)


            print(
                "Admin created"
            )



        await session.commit()



async def main():

    print(
        "Creating admin..."
    )


    await create_admin()


    print(
        "Done"
    )



if __name__ == "__main__":

    asyncio.run(main())

import asyncio
import os
import sys
from datetime import datetime


# добавляем app в PYTHONPATH
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../app"
        )
    )
)


from database import async_session
from models import Server
from sqlalchemy import select


SERVERS = [

    {
        "name": "Server 234",
        "domain": "234.com19.cc",
        "ip": "185.230.88.20"
    },

    {
        "name": "Server 239",
        "domain": "239.com19.cc",
        "ip": "185.230.88.39"
    },

    {
        "name": "Server 251",
        "domain": "251.com19.cc",
        "ip": "185.230.88.66"
    }

]


async def seed_servers():

    async with async_session() as session:

        for item in SERVERS:


            result = await session.execute(
                select(Server).where(
                    Server.domain == item["domain"]
                )
            )


            server = result.scalar_one_or_none()


            if server:

                print(
                    f"SKIP: {item['domain']} already exists"
                )

                continue



            server = Server(
                name=item["name"],
                domain=item["domain"],
                ip=item["ip"],
                active=True,
                created_at=datetime.utcnow()
            )


            session.add(server)


            print(
                f"ADD: {item['domain']}"
            )



        await session.commit()



async def main():

    print(
        "Starting database seed..."
    )

    await seed_servers()

    print(
        "Seed complete"
    )



if __name__ == "__main__":

    asyncio.run(main())

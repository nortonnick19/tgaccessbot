import asyncio

from database import async_session
from models import Server


servers = [
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


async def main():

    async with async_session() as session:

        for item in servers:

            server = Server(
                name=item["name"],
                domain=item["domain"],
                ip=item["ip"]
            )

            session.add(server)

        await session.commit()


asyncio.run(main())

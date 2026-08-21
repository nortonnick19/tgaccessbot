import asyncio
import logging


logger = logging.getLogger("firewall")


IPSET_MAP = {
    1: "wl_234",
    2: "wl_239",
    3: "wl_251",
}


IPSET_BIN = "/usr/sbin/ipset"


IPSET_SAVE_FILE = "/etc/iptables/ipsets"



async def run_command(command):

    try:

        process = await asyncio.create_subprocess_exec(

            *command,

            stdout=asyncio.subprocess.PIPE,

            stderr=asyncio.subprocess.PIPE

        )


        stdout, stderr = await process.communicate()


        if process.returncode != 0:

            logger.error(
                "Command failed: %s %s",
                command,
                stderr.decode()
            )

            return False


        return True



    except Exception as e:

        logger.exception(e)

        return False





async def save_ipsets():

    try:

        process = await asyncio.create_subprocess_exec(

            IPSET_BIN,

            "save",

            stdout=asyncio.subprocess.PIPE

        )


        stdout, _ = await process.communicate()


        if process.returncode != 0:

            return False



        with open(
            IPSET_SAVE_FILE,
            "wb"
        ) as f:

            f.write(stdout)



        logger.info(
            "ipset database saved"
        )


        return True



    except Exception as e:

        logger.exception(e)

        return False





def get_ipset(server_id):

    return IPSET_MAP.get(
        int(server_id)
    )





async def add_ip_to_firewall(
    server_id: int,
    ip: str
):


    ipset = get_ipset(
        server_id
    )


    if not ipset:

        logger.error(
            "Unknown server id %s",
            server_id
        )

        return False




    result = await run_command(

        [

            IPSET_BIN,

            "add",

            ipset,

            ip,

            "-exist"

        ]

    )



    if result:

        await save_ipsets()


        logger.info(

            "Firewall whitelist added %s -> %s",

            ip,

            ipset

        )


    return result






async def remove_ip_from_firewall(
    server_id:int,
    ip:str
):


    ipset = get_ipset(
        server_id
    )


    if not ipset:

        return False



    result = await run_command(

        [

            IPSET_BIN,

            "del",

            ipset,

            ip

        ]

    )



    # если уже удален
    if not result:

        logger.info(
            "IP already removed %s",
            ip
        )

        return True



    await save_ipsets()


    logger.info(

        "Firewall whitelist removed %s -> %s",

        ip,

        ipset

    )


    return True

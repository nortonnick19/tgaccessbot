import asyncio
import logging


logger = logging.getLogger(__name__)


IPSET_MAP = {

    1: "wl_234",

    2: "wl_239",

    3: "wl_251"

}


IPSET_BIN = "/usr/sbin/ipset"



async def _run_ipset(command: list):

    try:

        process = await asyncio.create_subprocess_exec(

            *command,

            stdout=asyncio.subprocess.PIPE,

            stderr=asyncio.subprocess.PIPE

        )


        stdout, stderr = await process.communicate()


        if process.returncode != 0:

            error = stderr.decode().strip()

            logger.error(
                f"ipset error: {error}"
            )

            return False


        return True


    except Exception as e:

        logger.exception(e)

        return False





async def add_ip_to_firewall(
    server_id: int,
    ip: str
):

    ipset_name = IPSET_MAP.get(
        server_id
    )


    if not ipset_name:

        logger.error(
            f"Unknown server id {server_id}"
        )

        return False



    command = [

        IPSET_BIN,

        "add",

        ipset_name,

        ip,

        "-exist"

    ]



    result = await _run_ipset(
        command
    )


    if result:

        logger.info(
            f"Firewall whitelist: {ip} -> {ipset_name}"
        )


    return result





async def remove_ip_from_firewall(
    server_id: int,
    ip: str
):

    ipset_name = IPSET_MAP.get(
        server_id
    )


    if not ipset_name:

        logger.error(
            f"Unknown server id {server_id}"
        )

        return False



    command = [

        IPSET_BIN,

        "del",

        ipset_name,

        ip

    ]



    result = await _run_ipset(
        command
    )


    if result:

        logger.info(
            f"Firewall removed: {ip} -> {ipset_name}"
        )

    else:

        # IP уже отсутствует = считаем удаленным

        logger.info(
            f"Firewall already clean: {ip}"
        )

        return True



    return True

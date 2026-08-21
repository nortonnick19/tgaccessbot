import json
import time
import re
import logging
import subprocess
from pathlib import Path

import requests
import geoip2.database


# =====================================================
# PATHS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

CONFIG_FILE = BASE_DIR / "config.json"

GEOIP_FILE = (
    BASE_DIR /
    "geoip" /
    "GeoLite2-Country.mmdb"
)


# =====================================================
# CONFIG
# =====================================================

with open(CONFIG_FILE) as f:
    config = json.load(f)


API_URL = config["api_url"]

AGENT_KEY = config["agent_key"]

COOLDOWN = config.get(
    "cooldown",
    300
)


# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


logger = logging.getLogger(
    "tgaccess-relay"
)


# =====================================================
# GEOIP
# =====================================================

geo_reader = geoip2.database.Reader(
    GEOIP_FILE
)


def get_country(ip):

    try:

        result = geo_reader.country(ip)

        name = (
            result.country.name
            or
            "Unknown"
        )

        code = (
            result.country.iso_code
            or
            ""
        )


        if code:
            return f"{name} ({code})"


        return name


    except Exception:

        return "Unknown"



# =====================================================
# SERVER CACHE
# =====================================================

servers = {}

last_refresh = 0


SERVER_REFRESH = 300



def load_servers():

    global servers
    global last_refresh


    now = time.time()


    if (
        now - last_refresh
        <
        SERVER_REFRESH
    ):
        return


    try:


        r = requests.get(

            API_URL.replace(
                "/access/event",
                "/relay/servers"
            ),

            headers={

                "X-Agent-Key":
                    AGENT_KEY

            },

            timeout=5

        )


        data = r.json()


        servers = {}


        for s in data:


            port = str(
                s["rdp_port"]
            )


            servers[port] = s



        last_refresh = now


        logger.info(
            "Servers refreshed: %s",
            servers
        )



    except Exception as e:


        logger.error(
            "Server refresh error: %s",
            e
        )




# =====================================================
# IPSET
# =====================================================

IPSET_BIN = "/usr/sbin/ipset"



def is_whitelisted(
    ip,
    ipset
):

    try:


        result = subprocess.run(

            [
                IPSET_BIN,
                "test",
                ipset,
                ip
            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL

        )


        return result.returncode == 0



    except Exception as e:


        logger.error(
            "ipset error: %s",
            e
        )


        return False




# =====================================================
# CACHE
# =====================================================

sent_cache = {}



def already_sent(
    server_id,
    ip
):


    key = (
        server_id,
        ip
    )


    now = time.time()



    if key in sent_cache:


        if (
            now -
            sent_cache[key]
            <
            COOLDOWN
        ):

            return True



    sent_cache[key] = now


    return False





# =====================================================
# PARSER
# =====================================================


def parse_connection(line):


    ip_match = re.search(

        r"SRC=([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)",

        line

    )


    port_match = re.search(

        r"DPT=(\d+)",

        line

    )



    if not ip_match:
        return None



    if not port_match:
        return None



    ip = ip_match.group(1)

    port = port_match.group(1)



    load_servers()



    server = servers.get(
        port
    )



    if not server:

        return None



    return {

        "ip": ip,

        "port": port,

        "server": server

    }





# =====================================================
# SEND EVENT
# =====================================================


def send_event(
    connection
):


    ip = connection["ip"]

    server = connection["server"]


    server_id = server["id"]


    if already_sent(
        server_id,
        ip
    ):

        logger.info(
            "Duplicate ignored %s -> %s",
            ip,
            server["name"]
        )

        return



    country = get_country(
        ip
    )



    payload = {

        "server_id":
            server_id,


        "username":
            "unknown",


        "source_ip":
            ip,


        "country":
            country,


        "event_type":
            "RDP_CONNECTION_ATTEMPT",


        "reason":
            "IP_NOT_WHITELISTED"

    }




    try:


        r = requests.post(

            API_URL,

            json=payload,

            headers={

                "X-Agent-Key":
                    AGENT_KEY

            },

            timeout=5

        )


        logger.info(

            "Sent %s:%s -> %s %s",

            ip,

            connection["port"],

            server["name"],

            r.text

        )



    except Exception as e:


        logger.error(
            "API error: %s",
            e
        )





# =====================================================
# WATCH
# =====================================================


def watch():


    logger.info(
        "TG Access Relay started"
    )


    process = subprocess.Popen(

        [
            "journalctl",
            "-k",
            "-f",
            "-o",
            "cat"
        ],

        stdout=subprocess.PIPE,

        stderr=subprocess.DEVNULL,

        text=True,

        bufsize=1

    )



    for line in process.stdout:



        if (
            "TGACCESS_RDP"
            not in line
        ):

            continue




        connection = parse_connection(
            line
        )



        if not connection:

            continue



        ip = connection["ip"]

        server = connection["server"]



        logger.info(

            "Connection %s:%s -> %s",

            ip,

            connection["port"],

            server["name"]

        )



        if is_whitelisted(

            ip,

            server["ipset_name"]

        ):


            logger.info(

                "Allowed IP ignored %s -> %s",

                ip,

                server["name"]

            )

            continue



        send_event(
            connection
        )





# =====================================================
# START
# =====================================================


if __name__ == "__main__":

    try:

        watch()


    except KeyboardInterrupt:

        logger.info(
            "Stopped"
        )

import logging
import subprocess

from datetime import datetime, timedelta

from aiogram import Router
from aiogram.types import CallbackQuery

from sqlalchemy import select

from database import async_session

from models import (
    AccessRequest,
    Whitelist,
    AuditLog,
    Server
)


router = Router()


logger = logging.getLogger(
    "access-handler"
)


WHITELIST_DAYS = 14



# =====================================================
# IPSET FUNCTIONS
# =====================================================

def add_ip_to_ipset(
    ipset_name,
    ip
):

    try:

        subprocess.run(

            [
                "ipset",
                "add",
                ipset_name,
                ip,
                "-exist"
            ],

            check=True,

            capture_output=True

        )


        logger.info(
            "Firewall whitelist: %s -> %s",
            ip,
            ipset_name
        )


        return True


    except Exception as e:


        logger.error(
            "ipset add error: %s",
            e
        )


        return False





def remove_ip_from_ipset(
    ipset_name,
    ip
):

    try:

        subprocess.run(

            [
                "ipset",
                "del",
                ipset_name,
                ip
            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL

        )


        logger.info(
            "Firewall removed: %s -> %s",
            ip,
            ipset_name
        )


    except Exception as e:


        logger.error(
            "ipset delete error: %s",
            e
        )





# =====================================================
# CALLBACK HANDLER
# =====================================================

@router.callback_query()
async def access_buttons(

    callback: CallbackQuery

):


    if not callback.data:

        return



    try:

        action, request_id = callback.data.split(":")

        request_id = int(request_id)


    except Exception:


        await callback.answer(
            "Invalid request"
        )

        return





    async with async_session() as session:



        result = await session.execute(

            select(AccessRequest)

            .where(
                AccessRequest.id == request_id
            )

        )


        request = (
            result
            .scalar_one_or_none()
        )



        if not request:


            await callback.answer(
                "Request not found"
            )

            return





        server_result = await session.execute(

            select(Server)

            .where(
                Server.id == request.server_id
            )

        )


        server = (
            server_result
            .scalar_one_or_none()
        )





        # =============================================
        # APPROVE
        # =============================================

        if action == "approve":



            expires = (
                datetime.utcnow()
                +
                timedelta(days=WHITELIST_DAYS)
            )



            request.status = "APPROVED"


            request.approved_by = str(
                callback.from_user.id
            )


            request.approved_at = (
                datetime.utcnow()
            )



            # Проверяем существующий IP

            existing_result = await session.execute(

                select(Whitelist)

                .where(

                    Whitelist.server_id ==
                    request.server_id,

                    Whitelist.ip ==
                    request.source_ip

                )

            )


            existing = (
                existing_result
                .scalar_one_or_none()
            )



            if existing:


                existing.expires_at = expires

                existing.username = (
                    request.username
                )


                logger.info(
                    "Whitelist renewed %s",
                    request.source_ip
                )


            else:


                whitelist = Whitelist(

                    server_id=request.server_id,

                    ip=request.source_ip,

                    username=request.username,

                    permanent=False,

                    expires_at=expires

                )


                session.add(
                    whitelist
                )





            # Firewall

            if server and server.ipset_name:


                add_ip_to_ipset(

                    server.ipset_name,

                    request.source_ip

                )





            log = AuditLog(

                server_id=request.server_id,

                action="APPROVE",

                details=(

                    f"{request.source_ip} "
                    f"expires {expires}"

                ),

                user=str(
                    callback.from_user.id
                )

            )


            session.add(log)





            await callback.message.edit_text(

                callback.message.text

                +

                "\n\n✅ <b>APPROVED</b>\n"

                +

                f"⏳ Valid until: "
                f"<b>{expires.strftime('%d.%m.%Y %H:%M')}</b>",

                reply_markup=None

            )







        # =============================================
        # BLOCK
        # =============================================

        elif action == "block":



            request.status = "BLOCKED"



            log = AuditLog(

                server_id=request.server_id,

                action="BLOCK",

                details=request.source_ip,

                user=str(
                    callback.from_user.id
                )

            )


            session.add(log)





            await callback.message.edit_text(

                callback.message.text

                +

                "\n\n⛔ <b>BLOCKED</b>",

                reply_markup=None

            )








        # =============================================
        # DELETE
        # =============================================

        elif action == "delete":



            log = AuditLog(

                server_id=request.server_id,

                action="DELETE",

                details=request.source_ip,

                user=str(
                    callback.from_user.id
                )

            )


            session.add(log)



            await session.delete(
                request
            )



            await callback.message.delete()





        await session.commit()



    await callback.answer(
        "Done"
    )

from datetime import datetime
import logging


from aiogram import Router, F
from aiogram.types import CallbackQuery


from sqlalchemy import select, delete


from database import async_session


from models import (
    AccessRequest,
    Whitelist,
    AuditLog,
    Server
)


from services.firewall import (
    add_ip_to_firewall,
    remove_ip_from_firewall
)



router = Router()


logger = logging.getLogger(__name__)





@router.callback_query(
    F.data.startswith("approve:")
)
async def approve_access(
    callback: CallbackQuery
):

    request_id = int(
        callback.data.split(":")[1]
    )


    async with async_session() as session:


        result = await session.execute(

            select(AccessRequest)
            .where(
                AccessRequest.id == request_id
            )

        )


        request = result.scalar_one_or_none()


        if not request:

            await callback.answer(
                "Request not found",
                show_alert=True
            )

            return



        if request.status != "WAITING":

            await callback.answer(
                "Already processed",
                show_alert=True
            )

            return



        request.status = "APPROVED"

        request.approved_by = str(
            callback.from_user.id
        )

        request.approved_at = datetime.utcnow()



        whitelist = Whitelist(

            server_id=request.server_id,

            ip=request.source_ip,

            username=request.username,

            permanent=True

        )


        session.add(
            whitelist
        )



        audit = AuditLog(

            server_id=request.server_id,

            action="APPROVE_ACCESS",

            details=f"Added {request.source_ip}",

            user=str(
                callback.from_user.id
            )

        )


        session.add(
            audit
        )


        await session.commit()



    firewall = await add_ip_to_firewall(

        request.server_id,

        request.source_ip

    )



    status = (

        "✅ Firewall updated"

        if firewall

        else

        "❌ Firewall failed"

    )



    await callback.message.edit_text(

        callback.message.text

        +

        "\n\n"

        +

        "✅ <b>APPROVED</b>\n"

        +

        status

    )


    await callback.answer()







@router.callback_query(
    F.data.startswith("delete:")
)
async def delete_access(
    callback: CallbackQuery
):


    request_id = int(
        callback.data.split(":")[1]
    )


    async with async_session() as session:


        result = await session.execute(

            select(AccessRequest)

            .where(
                AccessRequest.id == request_id
            )

        )


        request = result.scalar_one_or_none()


        if not request:

            await callback.answer(
                "Not found",
                show_alert=True
            )

            return



        await session.execute(

            delete(Whitelist)

            .where(

                Whitelist.server_id == request.server_id,

                Whitelist.ip == request.source_ip

            )

        )



        request.status = "DELETED"



        audit = AuditLog(

            server_id=request.server_id,

            action="DELETE_ACCESS",

            details=f"Removed {request.source_ip}",

            user=str(
                callback.from_user.id
            )

        )


        session.add(
            audit
        )


        await session.commit()




    firewall = await remove_ip_from_firewall(

        request.server_id,

        request.source_ip

    )



    status = (

        "🛡 Firewall removed"

        if firewall

        else

        "⚠ Firewall error"

    )



    await callback.message.edit_text(

        callback.message.text

        +

        "\n\n"

        +

        "🗑 <b>DELETED</b>\n"

        +

        status

    )


    await callback.answer()

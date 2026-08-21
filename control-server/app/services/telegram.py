import logging

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


logger = logging.getLogger(
    "telegram-service"
)



async def send_access_request(

    bot,

    chat_id: int,

    request_id: int,

    server_name: str,

    source_ip: str,

    country: str

):


    text = (

        "🚨 <b>RDP ACCESS REQUEST</b>\n\n"

        f"🖥 Server: <b>{server_name}</b>\n"

        f"🌐 IP: <code>{source_ip}</code>\n"

        f"🌍 Country: <b>{country}</b>\n\n"

        "⚠️ Status: "
        "<b>NOT WHITELISTED</b>"

    )



    keyboard = InlineKeyboardMarkup(

        inline_keyboard=[

            [

                InlineKeyboardButton(

                    text="✅ APPROVE",

                    callback_data=f"approve:{request_id}"

                ),


                InlineKeyboardButton(

                    text="⛔ BLOCK",

                    callback_data=f"block:{request_id}"

                )

            ],


            [

                InlineKeyboardButton(

                    text="🗑 DELETE",

                    callback_data=f"delete:{request_id}"

                )

            ]

        ]

    )



    try:


        message = await bot.send_message(

            chat_id=chat_id,

            text=text,

            reply_markup=keyboard

        )


        logger.info(

            "Telegram notification sent: %s",

            request_id

        )


        return message



    except Exception as e:


        logger.error(

            "Telegram send error %s: %s",

            request_id,

            e

        )


        return None

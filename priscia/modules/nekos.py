import os

import nekos
import requests
from telegram import ParseMode

from priscia import dispatcher
from priscia.modules.disable import DisableAbleCommandHandler


def neko(update, context):
    message = update.effective_message
    args = context.args
    flag = args[0]
    query = args[1]
    img = nekos.img(query)
    try:
        if flag == "-i":
            message.reply_photo(photo=img, parse_mode=ParseMode.MARKDOWN)
        elif flag == "-d":
            message.reply_document(document=img, parse_mode=ParseMode.MARKDOWN)
        elif flag == "-s":
            stkr = "sticker.webp"
            x = open(stkr, "wb")
            x.write(requests.get(img).content)
            message.reply_sticker(sticker=open(stkr, "rb"))
            os.remove("sticker.webp")
        elif flag == "-v":
            message.reply_video(video=img, parse_mode=ParseMode.MARKDOWN)
        else:
            message.reply_text("Put flags correctly!!!")
    except Exception as excp:
        message.reply_text(f"Failed to find image. Error: {excp}")


__help__ = """
× /neko <flags> <query>: Get random images from [Nekos API](nekos.life)
*Available flags:*
-i = send as image
-d = send as document(full resolution)
-s = send as sticker
-v = send as video(only for some query)
*Available query:*
Check this : [List Query](https://telegra.ph/List-Query-of-Nekos-01-19)
"""

__mod_name__ = "Nekos"

NEKO_HANDLER = DisableAbleCommandHandler("neko", neko)

dispatcher.add_handler(NEKO_HANDLER)

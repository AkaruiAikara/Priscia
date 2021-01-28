import datetime
import html
import os
import platform
import subprocess
import sys
import time
import traceback
from platform import python_version

import requests
import speedtest
from psutil import boot_time, cpu_percent, disk_usage, virtual_memory
from pyrogram import __version__ as __pyro__
from spamwatch import __version__ as __sw__
from telegram import ParseMode, __version__
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters
from telethon import __version__ as __tltn__

from priscia import MESSAGE_DUMP, OWNER_ID, dispatcher
from priscia.modules.helper_funcs.alternate import send_message
from priscia.modules.helper_funcs.filters import CustomFilters


def ping(update, context):
    msg = update.effective_message
    start_time = time.time()
    message = msg.reply_text("Pinging...")
    end_time = time.time()
    ping_time = round((end_time - start_time) * 1000, 3)
    message.edit_text(
        "*Pong!!!*\n`{}ms`".format(ping_time), parse_mode=ParseMode.MARKDOWN
    )


# Kanged from PaperPlane Extended userbot
def speed_convert(size):
    """
    Hi human, you can't read bytes?
    """
    power = 2 ** 10
    zero = 0
    units = {0: "", 1: "Kb/s", 2: "Mb/s", 3: "Gb/s", 4: "Tb/s"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"


def get_bot_ip(update, context):
    """Sends the bot's IP address, so as to be able to ssh in if necessary.
    OWNER ONLY.
    """
    res = requests.get("http://ipinfo.io/ip")
    update.message.reply_text(res.text)


def speedtst(update, context):
    chat = update.effective_chat
    message = update.effective_message
    edit_text = context.bot.editMessageText
    ed_msg = message.reply_text("Running high speed test . . .")
    test = speedtest.Speedtest()
    edit_text("Looking for best server . . .", chat.id, ed_msg.message_id)
    test.get_best_server()
    edit_text("Downloading . . .", chat.id, ed_msg.message_id)
    test.download()
    edit_text("Uploading . . .", chat.id, ed_msg.message_id)
    test.upload()
    edit_text("Finalizing . . .", chat.id, ed_msg.message_id)
    test.results.share()
    result = test.results.dict()
    edit_text(
        "Download "
        f"{speed_convert(result['download'])} \n"
        "Upload "
        f"{speed_convert(result['upload'])} \n"
        "Ping "
        f"{result['ping']} \n"
        "ISP "
        f"{result['client']['isp']}",
        chat.id,
        ed_msg.message_id,
    )


def system_status(update, context):
    uptime = datetime.datetime.fromtimestamp(boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    status = "<b>======[ SYSTEM INFO ]======</b>\n\n"
    status += "<b>System uptime:</b> <code>" + str(uptime) + "</code>\n"

    uname = platform.uname()
    status += "<b>System:</b> <code>" + str(uname.system) + "</code>\n"
    status += "<b>Node name:</b> <code>" + str(uname.node) + "</code>\n"
    status += "<b>Release:</b> <code>" + str(uname.release) + "</code>\n"
    status += "<b>Version:</b> <code>" + str(uname.version) + "</code>\n"
    status += "<b>Machine:</b> <code>" + str(uname.machine) + "</code>\n"
    status += "<b>Processor:</b> <code>" + str(uname.processor) + "</code>\n\n"

    mem = virtual_memory()
    cpu = cpu_percent()
    disk = disk_usage("/")
    status += "<b>CPU usage:</b> <code>" + str(cpu) + " %</code>\n"
    status += "<b>Ram usage:</b> <code>" + str(mem[2]) + " %</code>\n"
    status += "<b>Storage used:</b> <code>" + str(disk[3]) + " %</code>\n\n"
    status += "<b>Python version:</b> <code>" + python_version() + "</code>\n"
    status += "<b>PTB version:</b> <code>" + str(__version__) + "</code>\n"
    status += "<b>Telethon version:</b> <code>" + str(__tltn__) + "</code>\n"
    status += "<b>Pyrogram version:</b> <code>" + str(__pyro__) + "</code>\n"
    status += "<b>Spamwatch API:</b> <code>" + str(__sw__) + "</code>\n"
    context.bot.sendMessage(update.effective_chat.id, status, parse_mode=ParseMode.HTML)


def leavechat(update, context):
    args = context.args
    msg = update.effective_message
    if args:
        chat_id = int(args[0])

    else:
        msg.reply_text("Bro.. Give Me ChatId And boom!!")
    try:
        titlechat = context.bot.get_chat(chat_id).title
        context.bot.sendMessage(
            chat_id,
            "I'm here trying to survive, but this world is too cruel, goodbye everyone 😌",
        )
        context.bot.leaveChat(chat_id)
        msg.reply_text("I have left the group {}".format(titlechat))

    except BadRequest as excp:
        if excp.message == "bot is not a member of the supergroup chat":
            msg = update.effective_message.reply_text(
                "I'Am not Joined The Group, Maybe You set wrong id or I Already Kicked out"
            )

        else:
            return


def gitpull(update, context):
    msg = update.effective_message
    args = msg.text.split(None, 1)
    branch = args[1]
    sent_msg = msg.reply_text("Pulling all changes from remote...")
    subprocess.Popen(f"git pull {branch}", stdout=subprocess.PIPE, shell=True)

    sent_msg_text = (
        sent_msg.text
        + "\n\nChanges pulled... I guess..\nContinue to restart with /reboot "
    )
    sent_msg.edit_text(sent_msg_text)


def restart(update, context):
    user = update.effective_message.from_user

    update.effective_message.reply_text(
        "Starting a new instance and shutting down this one"
    )

    if MESSAGE_DUMP:
        datetime_fmt = "%H:%M - %d-%m-%Y"
        current_time = datetime.datetime.utcnow().strftime(datetime_fmt)
        message = (
            f"<b>Bot Restarted </b>"
            f"<b>By :</b> <code>{html.escape(user.first_name)}</code>"
            f"<b>\nDate Bot Restart : </b><code>{current_time}</code>"
        )
        context.bot.send_message(
            chat_id=MESSAGE_DUMP,
            text=message,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    os.system("bash start")


def evaluator(update, context):
    msg = update.effective_message
    if msg.text:
        args = msg.text.split(None, 1)
        code = args[1]
        try:
            exec(code)
        except BaseException:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(
                etype=exc_type, value=exc_obj, tb=exc_tb
            )
            send_message(
                update.effective_message,
                "**Execute**\n`{}`\n\n*Failed:*\n```{}```".format(
                    code, "".join(errors)
                ),
                parse_mode="markdown",
            )


def executor(update, context):
    msg = update.effective_message
    if msg.text:
        args = msg.text.split(None, 1)
        code = args[1]
        run = subprocess.run(code, stdout=subprocess.PIPE, shell=True)
        output = run.stdout.decode()
        msg.reply_text(
            f"*Input:*\n`{code}`\n\n*Output:*\n`{output}`",
            parse_mode=ParseMode.MARKDOWN,
        )


IP_HANDLER = CommandHandler("ip", get_bot_ip, filters=Filters.user(OWNER_ID))
PING_HANDLER = CommandHandler("ping", ping, filters=CustomFilters.sudo_filter)
SPEED_HANDLER = CommandHandler("speedtest", speedtst, filters=CustomFilters.sudo_filter)
SYS_STATUS_HANDLER = CommandHandler(
    "sysinfo", system_status, filters=CustomFilters.sudo_filter
)
LEAVECHAT_HANDLER = CommandHandler(
    ["leavechat", "leavegroup", "leave"],
    leavechat,
    pass_args=True,
    filters=CustomFilters.sudo_filter,
)
GITPULL_HANDLER = CommandHandler("gitpull", gitpull, filters=CustomFilters.sudo_filter)
RESTART_HANDLER = CommandHandler("reboot", restart, filters=CustomFilters.sudo_filter)
EVAL_HANDLER = CommandHandler("eval", evaluator, filters=Filters.user(OWNER_ID))
EXEC_HANDLER = CommandHandler("exec", executor, filters=Filters.user(OWNER_ID))

dispatcher.add_handler(IP_HANDLER)
dispatcher.add_handler(SPEED_HANDLER)
dispatcher.add_handler(PING_HANDLER)
dispatcher.add_handler(SYS_STATUS_HANDLER)
dispatcher.add_handler(LEAVECHAT_HANDLER)
dispatcher.add_handler(GITPULL_HANDLER)
dispatcher.add_handler(RESTART_HANDLER)
dispatcher.add_handler(EVAL_HANDLER)
dispatcher.add_handler(EXEC_HANDLER)

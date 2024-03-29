""" Commands interface """
from loguru import logger
from telegram import Bot
from telegram import BotCommandScopeAllChatAdministrators
from telegram import BotCommandScopeAllGroupChats
from telegram import BotCommandScopeAllPrivateChats
from telegram import BotCommandScopeChat

from bot.admins import ADMINS


async def clear_bot(bot: Bot):
    """deletes previous commands"""

    await bot.delete_my_commands(BotCommandScopeAllPrivateChats())
    await bot.delete_my_commands(BotCommandScopeAllGroupChats())
    await bot.delete_my_commands(BotCommandScopeAllChatAdministrators())
    logger.debug("User commands were cleared.")


all_commands = [
    ("start", "Start bot 🚀"),
    ("language", "Set language 🏴‍☠️"),
    ("stop", "Stop bot 🚫"),
]

admin_commands = [
    ("admin", "Admin console 🕹"),
    ("id", "current chat_id 💳"),
    ("time", "server time 🕡"),
]


async def set_bot_commands(bot: Bot):
    """create commands lists for different chats and users"""

    # admins
    for chat_id in ADMINS:
        try:
            await bot.set_my_commands(
                all_commands + admin_commands, scope=BotCommandScopeChat(chat_id)
            )
        except Exception as error:
            logger.error(
                f"Setting commands for chat_id: {chat_id}, failed with error: {error}"
            )

    # privat chats
    await bot.set_my_commands(all_commands, scope=BotCommandScopeAllPrivateChats())

    logger.debug("Command list was updated.")

from typing import Dict
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from bot.data import text
from bot.database import db_interface
from bot.handlers.utils import change_indent
from bot.handlers.utils import start_query
from bot.utils import send_msg_with_keyboard
from bot.utils import State
from bot.utils import User
from bot.utils import user_manager
from bot.utils.logs import log_message
from bot.utils.user_manager import QuestionType


def get_answer_id(msg: str) -> Optional[str]:
    # always return -1 if msg is not in choices
    choices: Dict[str, str] = {
        # type
        text["team_building"]: "Teambuilding",
        text["ice_breaker"]: "warm ups",
        text["timefiller"]: "Timefillers",
        # age
        text["6-12"]: "6-12",
        text["12+"]: "12+",
        # count
        text["up to 5"]: "up to 5",
        text["5-20"]: "5-20",
        text["20+"]: "20+",
        # place
        text["outside"]: "outside",
        text["inside"]: "inside",
        # props
        text["no"]: "no",
        text["yes"]: "yes",
    }

    return choices.get(msg)


async def save_answer(update: Update, question_type: QuestionType):
    chat_id = update.message.chat.id
    # lang = get_lang(update)

    answer_id = get_answer_id(update.message.text)
    user_manager.take_answer(chat_id, question_type, answer_id)


async def ask_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    # lang = get_lang(update)
    user_manager.create_user(User(chat_id, update.message.chat.username))

    user_manager.current_users[chat_id].set_flag(1)
    reply_keyboard = [
        [text["team_building"]],
        [text["ice_breaker"]],
        [text["timefiller"]],
        [text["any"], text["back"]],
    ]

    await send_msg_with_keyboard(update, context, text["ask_type"], reply_keyboard)
    return State.READ_TYPE


async def read_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_message(update)
    await save_answer(update, question_type=QuestionType.TYPE)
    return await ask_age(update, context)


async def ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        [text["6-12"], text["12+"]],
        [text["any"], text["back"]],
    ]
    await send_msg_with_keyboard(update, context, text["ask_age"], reply_keyboard)
    return State.READ_AGE


async def read_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_message(update)
    await save_answer(update, question_type=QuestionType.AGE)
    return await ask_amount(update, context)


async def ask_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        [text["up to 5"], text["5-20"], text["20+"]],
        [text["any"], text["back"]],
    ]
    await send_msg_with_keyboard(update, context, text["ask_amount"], reply_keyboard)
    return State.READ_AMOUNT


async def read_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_message(update)
    await save_answer(update, question_type=QuestionType.AMOUNT)
    return await ask_location(update, context)


async def ask_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        [text["outside"], text["inside"]],
        [text["any"], text["back"]],
    ]
    await send_msg_with_keyboard(update, context, text["ask_location"], reply_keyboard)
    return State.READ_LOCATION


async def read_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_message(update)
    await save_answer(update, question_type=QuestionType.LOCATION)
    return await ask_props(update, context)


async def ask_props(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    reply_keyboard = [
        [text["yes"], text["no"]],
        [text["any"], text["back"]],
    ]
    await send_msg_with_keyboard(update, context, text["ask_props"], reply_keyboard)
    return State.READ_PROPS


async def read_props(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_message(update)
    await save_answer(update, question_type=QuestionType.PROPS)
    return await result(update, context)


async def result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    # lang = get_lang(update)
    answers = user_manager.current_users[chat_id].answers
    games = db_interface.get_game_names(
        game_type=answers[QuestionType.TYPE],
        kids_age=answers[QuestionType.AGE],
        kids_amount=answers[QuestionType.AMOUNT],
        location=answers[QuestionType.LOCATION],
        props=answers[QuestionType.PROPS],
    )

    reply_keyboard = [[game_name[1]] for game_name in games]
    reply_keyboard.append([text["back"], text["menu"]])
    await send_msg_with_keyboard(update, context, text["answer"], reply_keyboard)
    return State.ANSWER


async def final_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_message(update)
    chat_id = update.message.chat.id
    # lang = get_lang(update)
    massage = update.message.text

    if massage == text["menu"]:
        user_manager.delete_user(chat_id)
        return await start_query(update, context)
    user_manager.current_users[chat_id].set_flag(7)

    description = db_interface.get_game_description(massage)
    description = change_indent(description)
    reply_keyboard = [[text["back"], text["menu"]]]

    await send_msg_with_keyboard(update, context, description, reply_keyboard)
    return State.BACK_ANSWER

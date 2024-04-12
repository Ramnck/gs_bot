from asyncio import sleep

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from ..db.crud import stats
from ..logic.dont_care import Menu, get_count, set_count, set_dont_care, unset_dont_care
from ..settings import get_settings
from ..tools.formatter import mention_all, rand_dont_care, stats_format

router = Router()
settings = get_settings()


@router.message(Command(commands=["start"]))
async def start(msg: Message):
    await msg.answer("Тебе не понадобится этот бот")


@router.message(Command(commands=["help"]))
async def help(msg: Message):
    await msg.answer("Если ты не знаешь что это за бот значит он тебе не нужен")


@router.message(Command(commands=["info"]))
async def info(msg: Message, bot: Bot):
    user_stats = await stats.get_or_create(msg.from_user.id)
    res = stats_format(user_stats)
    answer = await msg.reply(res, parse_mode="HTML")
    if msg.chat.id == settings.ANGAR_ID:
        await sleep(10)
        await bot.delete_message(msg.chat.id, answer.message_id)
        await bot.delete_message(msg.chat.id, msg.message_id)


@router.message(Command(commands=["happynewyear"]))
async def new_year(msg: Message, bot: Bot):
    await bot.send_message(
        settings.ANGAR_ID,
        "Ангар dev поздравляет вас с Новым Годом и дарит вам этого ебейшего бота. С Новым годом, братья ❤️‍🔥🥳🎉",
    )


@router.message(Command(commands=["infoall"]))
async def info_all(msg: Message, bot: Bot):
    if msg.chat.id == settings.ANGAR_ID:
        answer = await msg.reply("В ангар срать не буду, спроси в лс")
        await sleep(10)
        await bot.delete_message(msg.chat.id, answer.message_id)
        await bot.delete_message(msg.chat.id, msg.message_id)
    else:
        mentions = await mention_all(bot)
        for mention in mentions:
            user_stats = await stats.get_or_create(
                int(mention[mention.index("id=") + 3 : mention.index('">')])
            )
            res = stats_format(user_stats)
            res = res.replace("Твоя активность, сучка", "Активность " + mention)
            await msg.reply(res, parse_mode="HTML")


@router.message(F.text.contains("@all"))
async def all_command(msg: Message, bot: Bot):
    text = await mention_all(bot)
    text = " ".join(text)
    await msg.answer(text, parse_mode="HTML")


@router.message(Command(commands=["poh"]))
async def dont_care(msg: Message, bot: Bot):
    keyboard = InlineKeyboardBuilder()
    members = await mention_all(bot)
    buttons = []
    for mention in members:
        user_name, user_id = (
            mention[mention.index('">') + 2 : mention.index("</")],
            mention[mention.index("id=") + 3 : mention.index('">')],
        )
        buttons.append(
            InlineKeyboardButton(text=user_name, callback_data=f"dont_care;{user_id}")
        )
    keyboard.row(*buttons, width=2)
    await bot.delete_message(msg.chat.id, msg.message_id)
    await msg.answer(
        "На кого похуй?", reply_markup=keyboard.as_markup(), parse_mode="html"
    )


@router.callback_query(F.data.startswith("dont_care"))
async def dont_care_call(call: CallbackQuery, bot: Bot):
    data = call.data.split(";")
    if data[1] == "839659710":
        await bot.answer_callback_query(call.id, text="А может лучше на тебя похуй??")
    else:
        status = await set_dont_care(call.message.chat.id, data[1])
        if status == "Already dont_care":
            await bot.answer_callback_query(call.id, text="И так уже похуй")
    await bot.delete_message(call.message.chat.id, call.message.message_id)


@router.message(Command(commands=["nepoh"]))
async def nedont_care(msg: Message, bot: Bot):
    keyboard = InlineKeyboardBuilder()
    members = await mention_all(bot)
    buttons = []
    for mention in members:
        user_name, user_id = (
            mention[mention.index('">') + 2 : mention.index("</")],
            mention[mention.index("id=") + 3 : mention.index('">')],
        )
        buttons.append(
            InlineKeyboardButton(text=user_name, callback_data=f"nedont_care;{user_id}")
        )
    keyboard.row(*buttons, width=2)
    await bot.delete_message(msg.chat.id, msg.message_id)
    await msg.answer(
        "На кого не похуй?", reply_markup=keyboard.as_markup(), parse_mode="html"
    )


@router.callback_query(F.data.startswith("nedont_care"))
async def nedont_care_call(call: CallbackQuery, bot: Bot):
    data = call.data.split(";")
    if data[1] == "839659710":
        await bot.answer_callback_query(call.id, text="На него и так не похуй")
    else:
        status = await unset_dont_care(call.message.chat.id, data[1])
        if status == "Already nedont_care":
            await bot.answer_callback_query(call.id, text="И так уже не похуй")
    await bot.delete_message(call.message.chat.id, call.message.message_id)


@router.callback_query(F.data == "+dont_care")
async def plus_dont_care(call: CallbackQuery, bot: Bot):
    chat_name = call.message.chat.id
    count = await get_count(chat_name)
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=rand_dont_care(), callback_data=f"+dont_care")
    await set_count(chat_name, count + 1)
    await call.message.edit_text(
        f"{rand_dont_care()}\nx {count+1}", reply_markup=keyboard.as_markup()
    )

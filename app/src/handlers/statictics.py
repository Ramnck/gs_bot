from aiogram import F, Router
from aiogram.types import Message

from ..logic.privacy import is_based
from ..logic.stats import analyze_talk, update_stats

router = Router()


@router.message(~F.func(lambda msg: is_based(msg)))
async def count_entities(msg: Message):
    await update_stats(msg)
    await analyze_talk(msg)

import asyncio
import logging
import re

import feedparser
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, func

from config import BOT_TOKEN, CHANNEL_ID, ADMIN_IDS, POLL_INTERVAL_MINUTES
from database import init_db, async_session, PostedArticle
from feeds import FEEDS
from translator import translate_to_uzbek

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("mma-uz-bot")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def strip_html(raw_html: str) -> str:
    """RSS description ichida keladigan <a>, <p> kabi HTML teglarni tozalaydi."""
    text = re.sub(r"<[^>]+>", "", raw_html or "")
    return text.strip()


async def is_already_posted(guid: str) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(PostedArticle.id).where(PostedArticle.guid == guid)
        )
        return result.scalar_one_or_none() is not None


async def mark_posted(source: str, guid: str, title: str):
    async with async_session() as session:
        session.add(PostedArticle(source=source, guid=guid, title=title))
        await session.commit()


async def is_bootstrap_needed() -> bool:
    """
    Bot birinchi marta ishga tushganda barcha manbalarda allaqachon mavjud
    bo'lgan (eski) yangiliklarni kanalga bir vaqtda tashlab yubormasligi uchun.
    Baza butunlay bo'sh bo'lsa - hozirgi feedlardagi hamma narsani faqat
    "ko'rilgan" deb belgilaymiz, hech narsa e'lon qilmaymiz. Shundan keyingi
    tekshiruvlarda faqat haqiqatan ham YANGI maqolalar e'lon qilinadi.
    """
    async with async_session() as session:
        result = await session.execute(select(PostedArticle.id).limit(1))
        return result.scalar_one_or_none() is None


def format_post(source: str, title_uz: str, summary_uz: str, link: str) -> str:
    return (
        f"🥋 <b>{title_uz}</b>\n\n"
        f"{summary_uz}\n\n"
        f"🔗 Manba: {source} | <a href=\"{link}\">to'liq o'qish</a>\n"
        f"#MMA #UFC"
    )


async def fetch_and_post():
    """Barcha manbalarni tekshiradi, yangi maqolalarni tarjima qilib kanalga yuboradi."""
    bootstrap = await is_bootstrap_needed()
    if bootstrap:
        logger.info("Birinchi ishga tushish aniqlandi - eski yangiliklar e'lon qilinmaydi, faqat belgilab qo'yiladi.")

    for feed_info in FEEDS:
        source_name = feed_info["name"]
        try:
            parsed = await asyncio.to_thread(feedparser.parse, feed_info["url"])
        except Exception as e:
            logger.error(f"{source_name} manbasini o'qishda xato: {e}")
            continue

        if parsed.bozo and not parsed.entries:
            logger.warning(f"{source_name}: feed o'qilmadi yoki bo'sh ({parsed.bozo_exception})")
            continue

        # Eskisidan yangisiga qarab yuboramiz - kanalda xronologik tartib saqlanadi
        entries = list(reversed(parsed.entries))

        for entry in entries:
            guid = entry.get("id") or entry.get("link")
            if not guid:
                continue

            if await is_already_posted(guid):
                continue

            title = (entry.get("title") or "").strip()

            if bootstrap:
                await mark_posted(source_name, guid, title)
                continue

            summary = strip_html(entry.get("summary") or entry.get("description") or "")
            link = entry.get("link", "")

            translated = await translate_to_uzbek(title, summary)
            post_text = format_post(source_name, translated["title"], translated["summary"], link)

            try:
                await bot.send_message(CHANNEL_ID, post_text, parse_mode="HTML")
                logger.info(f"Yuborildi [{source_name}]: {title}")
            except Exception as e:
                logger.error(f"Kanalga yuborishda xato: {e}")
                continue

            await mark_posted(source_name, guid, title)
            await asyncio.sleep(3)  # Telegram flood-limitga tushmaslik uchun kichik pauza


def is_admin(telegram_id: int) -> bool:
    return telegram_id in ADMIN_IDS


@dp.message(Command("status"))
async def cmd_status(message: Message):
    if not is_admin(message.from_user.id):
        return

    async with async_session() as session:
        total = (await session.execute(select(func.count()).select_from(PostedArticle))).scalar()

    await message.answer(
        "✅ Bot ishlamoqda.\n\n"
        f"📊 Jami e'lon qilingan: {total} ta\n"
        f"⏱ Tekshirish oralig'i: {POLL_INTERVAL_MINUTES} daqiqa\n"
        f"📡 Manbalar: {', '.join(f['name'] for f in FEEDS)}\n"
        f"📢 Kanal: {CHANNEL_ID}"
    )


@dp.message(Command("check"))
async def cmd_force_check(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🔄 Manbalar tekshirilmoqda...")
    await fetch_and_post()
    await message.answer("✅ Tekshiruv yakunlandi.")


async def main():
    await init_db()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(fetch_and_post, "interval", minutes=POLL_INTERVAL_MINUTES)
    scheduler.start()

    # Bot ishga tushgandan darhol keyin birinchi tekshiruvni ham bajaramiz
    asyncio.create_task(fetch_and_post())

    logger.info("MMA UZ bot ishga tushdi.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

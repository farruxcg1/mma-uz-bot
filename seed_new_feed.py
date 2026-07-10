"""
Botga yangi manba qo'shilganda, o'sha manbadagi HOZIRGI maqolalarni kanalga
yubormasdan, faqat "ko'rilgan" deb bazaga belgilab qo'yadi. Shundan keyingi
tekshiruvlarda o'sha manbadan faqat YANGI chiqadigan maqolalar e'lon qilinadi.

Ishlatish - RSS manba uchun (Railway'da mma-uz-bot xizmatining Console'ida):
    python seed_new_feed.py "MMA Fighting" https://www.mmafighting.com/rss/current

Ishlatish - scrape (HTML) manba uchun, parser nomini "scrape:" bilan bering:
    python seed_new_feed.py "SportUz UFC" scrape:sportuz_ufc:https://sportuz.tv/ufc/ufcnews
"""

import asyncio
import sys

import feedparser

from database import async_session, PostedArticle, init_db
from sqlalchemy import select
from scrapers import scrape as scrape_source


async def seed(source_name: str, feed_url: str):
    await init_db()

    if feed_url.startswith("scrape:"):
        _, parser_name, url = feed_url.split(":", 2)
        entries = await scrape_source(parser_name, url)
    else:
        parsed = feedparser.parse(feed_url)
        entries = parsed.entries

    if not entries:
        print(f"OGOHLANTIRISH: '{source_name}' manbasida hech qanday maqola topilmadi.")
        return

    added = 0
    async with async_session() as session:
        for entry in entries:
            guid = entry.get("id") or entry.get("link")
            if not guid:
                continue

            existing = await session.execute(
                select(PostedArticle.id).where(PostedArticle.guid == guid)
            )
            if existing.scalar_one_or_none() is not None:
                continue

            title = (entry.get("title") or "").strip()
            session.add(PostedArticle(source=source_name, guid=guid, title=title))
            added += 1

        await session.commit()

    print(f"Tayyor: '{source_name}' manbasidan {added} ta maqola 'ko'rilgan' deb belgilandi.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Ishlatish: python seed_new_feed.py \"Manba nomi\" https://feed-url")
        print("Yoki scrape uchun: python seed_new_feed.py \"Manba nomi\" scrape:parser_nomi:https://url")
        sys.exit(1)

    asyncio.run(seed(sys.argv[1], sys.argv[2]))
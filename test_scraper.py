"""
Scraper qanday ishlayotganini bazaga tegmasdan tekshirish uchun.

Ishlatish (Railway Console'da):
    python test_scraper.py sportuz_ufc https://sportuz.tv/ufc/ufcnews
"""

import asyncio
import sys

from scrapers import scrape


async def main(parser_name: str, url: str):
    items = await scrape(parser_name, url)
    print(f"Jami topildi: {len(items)} ta maqola\n")
    for item in items[:5]:
        print("=" * 60)
        print("Sarlavha:", item["title"])
        print("Havola:", item["link"])
        print("Rasm:", item.get("image"))
        print("Matn:", item["summary"][:200])


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Ishlatish: python test_scraper.py parser_nomi https://url")
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
"""
sportuz.tv sahifasidan HAQIQIY nima qaytayotganini ko'rish uchun.
Bot bloklanganmi (403/empty) yoki HTML tuzilishi boshqachami - shuni aniqlaydi.

Ishlatish:
    python debug_fetch.py https://sportuz.tv/ufc/ufcnews
"""

import asyncio
import sys

import httpx

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


async def main(url: str):
    async with httpx.AsyncClient(timeout=15, headers=HEADERS, follow_redirects=True) as client:
        response = await client.get(url)

    print(f"Status kod: {response.status_code}")
    print(f"Yakuniy URL: {response.url}")
    print(f"Javob uzunligi: {len(response.text)} belgi")
    print()

    text = response.text
    print("--- Birinchi 1500 belgi ---")
    print(text[:1500])
    print()

    for marker in ["imageboksufc", "ufc.tv/ufc/", "sportuz.tv/ufc/", "<img", "<a href"]:
        count = text.count(marker)
        print(f"'{marker}' necha marta uchradi: {count}")

    print()
    print("--- Birinchi 6 ta <a href misoli ---")
    import re
    for m in list(re.finditer(r'<a\s+[^>]*href="[^"]*"[^>]*>', text))[:6]:
        print(m.group(0))

    print()
    print("--- Birinchi 4 ta <img misoli ---")
    for m in list(re.finditer(r'<img[^>]*>', text))[:4]:
        print(m.group(0))

    print()
    print("--- '.html' bilan tugaydigan havolalar (10 tasi) ---")
    for m in list(re.finditer(r'<a\s+[^>]*href="[^"]*\.html"[^>]*>[^<]*', text))[:10]:
        print(m.group(0))
        print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Ishlatish: python debug_fetch.py https://url")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
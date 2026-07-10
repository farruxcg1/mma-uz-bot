"""
RSS bermaydigan o'zbekcha saytlar uchun maxsus scraperlar.
Har bir funksiya feedparser entry'siga o'xshash ro'yxat qaytaradi:
[{"id": ..., "link": ..., "title": ..., "summary": ..., "image": ...}, ...]

Muhim: bu saytlar dizaynini o'zgartirsa, scraper buzilishi mumkin - bu RSS'ga
qaraganda ko'proq parvarish talab qiladigan usul.
"""

import re
import logging

import httpx

logger = logging.getLogger("mma-uz-bot")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


async def _fetch_html(url: str) -> str:
    async with httpx.AsyncClient(timeout=15, headers=HEADERS, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


async def scrape_sportuz_ufc(url: str) -> list[dict]:
    """
    sportuz.tv/ufc/ufcnews sahifasidagi maqolalar ro'yxatini o'qiydi.
    Sahifada RSS yo'q, shuning uchun HTML'ni to'g'ridan-to'g'ri tahlil qilamiz.
    """
    html = await _fetch_html(url)

    # Har bir maqola: rasm -> sarlavha havolasi -> sana -> qisqa matn (<p>)
    pattern = re.compile(
        r'<img[^>]+src="(?P<image>https://sportuz\.tv/ufc/imageboksufc/[^"]+)"[^>]*>'
        r'.*?'
        r'<a[^>]+href="(?P<link>https://sportuz\.tv/ufc/\d+-[^"]+?\.html)"[^>]*>(?P<title>[^<]+)</a>'
        r'.*?'
        r'(?P<date>\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2})'
        r'.*?'
        r'<p[^>]*>(?P<summary>.*?)</p>',
        re.DOTALL,
    )

    results = []
    seen_links = set()
    for m in pattern.finditer(html):
        link = m.group("link")
        if link in seen_links:
            continue
        seen_links.add(link)

        title = re.sub(r"\s+", " ", m.group("title")).strip()
        summary = re.sub(r"<[^>]+>", "", m.group("summary"))
        summary = re.sub(r"\s+", " ", summary).strip()
        image = m.group("image")

        if not title or not link:
            continue

        results.append({
            "id": link,
            "link": link,
            "title": title,
            "summary": summary,
            "image": image,
        })

    if not results:
        logger.warning("SportUz UFC scraperi hech narsa topolmadi - sayt dizayni o'zgargan bo'lishi mumkin.")

    # Eskisidan yangisiga qarab qaytaramiz (sahifada eng yangisi tepada keladi)
    return list(reversed(results))


# Manba nomi -> scraper funksiyasi
SCRAPERS = {
    "sportuz_ufc": scrape_sportuz_ufc,
}


async def scrape(parser_name: str, url: str) -> list[dict]:
    func = SCRAPERS.get(parser_name)
    if not func:
        raise ValueError(f"Noma'lum scraper: {parser_name}")
    return await func(url)
"""
RSS bermaydigan o'zbekcha saytlar uchun maxsus scraperlar.
Har bir funksiya feedparser entry'siga o'xshash ro'yxat qaytaradi:
[{"id": ..., "link": ..., "title": ..., "summary": ..., "image": ...}, ...]

Muhim: bu saytlar dizaynini o'zgartirsa, scraper buzilishi mumkin - bu RSS'ga
qaraganda ko'proq parvarish talab qiladigan usul.
"""

import re
import html as html_lib
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


def _clean_text(raw: str) -> str:
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html_lib.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


async def scrape_sportuz_ufc(url: str) -> list[dict]:
    """
    sportuz.tv/ufc/ufcnews sahifasidagi maqolalar ro'yxatini o'qiydi.
    Aniq HTML teglariga (masalan <p>, <div class="...">) bog'lanib qolmaslik
    uchun, faqat ISHONCHLI qismlarga (rasm src va maqola havolasi) tayanib,
    ular orasidagi matnni pozitsiya bo'yicha ajratib olamiz. Shunday qilib,
    sayt HTML tuzilishini biroz o'zgartirsa ham scraper ishlashda davom etadi.
    """
    html = await _fetch_html(url)

    link_pattern = re.compile(
        r'<a[^>]+href="(https://sportuz\.tv/ufc/(\d+)-[^"]+\.html)"[^>]*>(.*?)</a>',
        re.DOTALL,
    )
    image_pattern = re.compile(
        r'<img[^>]+src="(https://sportuz\.tv/ufc/imageboksufc/[^"]+?\.(?:jpg|jpeg|png|webp))"',
        re.IGNORECASE,
    )

    images = [(m.start(), m.group(1)) for m in image_pattern.finditer(html)]
    links = list(link_pattern.finditer(html))

    articles = {}
    order = []

    for m in links:
        link, article_id, title_html = m.group(1), m.group(2), m.group(3)
        title = _clean_text(title_html)

        # "Batafsil..." havolasi ham xuddi shu maqolaga ishora qiladi -
        # sarlavha sifatida faqat mazmunli matnli birinchisini olamiz
        if not title or title.lower().startswith("batafsil"):
            continue
        if article_id in articles:
            continue

        image = None
        for img_pos, img_url in images:
            if img_pos < m.start():
                image = img_url
            else:
                break

        articles[article_id] = {
            "link": link,
            "title": title,
            "image": image,
            "title_end": m.end(),
        }
        order.append(article_id)

    results = []
    for article_id in order:
        art = articles[article_id]
        start = art["title_end"]
        next_link = link_pattern.search(html, pos=start)
        end = next_link.start() if next_link else min(start + 1000, len(html))

        summary = _clean_text(html[start:end])
        # Boshidagi sana/ko'rishlar sonini olib tashlaymiz (masalan "10.07.2026 16:57 1264")
        summary = re.sub(r"^\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}\s*\d*\s*", "", summary).strip()

        results.append({
            "id": art["link"],
            "link": art["link"],
            "title": art["title"],
            "summary": summary,
            "image": art["image"],
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
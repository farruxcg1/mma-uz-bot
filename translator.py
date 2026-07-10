import json

from anthropic import AsyncAnthropic

from config import ANTHROPIC_API_KEY

client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
AI_MODEL = "claude-haiku-4-5-20251001"


async def translate_to_uzbek(title: str, summary: str) -> dict:
    """
    Ingliz tilidagi MMA yangiligini o'zbek tiliga so'zma-so'z tarjima QILMAYDI -
    voqeani o'z so'zlari bilan, oddiy va tushunarli tilda qayta hikoya qiladi
    (xuddi sport sharhlovchisi do'stiga gapirib berayotgandek).

    AI sozlanmagan yoki xato bersa - original (ingliz) matnni qaytaradi,
    bot to'xtab qolmaydi.
    """
    if not client:
        return {"title": title, "summary": summary}

    try:
        response = await client.messages.create(
            model=AI_MODEL,
            max_tokens=400,
            system=(
                "Siz sport jurnalistisiz. Sizga ingliz tilidagi MMA/UFC yangiligi "
                "beriladi. Vazifangiz - uni o'zbek tiliga SO'ZMA-SO'Z TARJIMA QILISH "
                "EMAS, balki o'qib, mazmunini tushunib, xuddi do'stingizga gapirib "
                "berayotgandek O'Z SO'ZLARINGIZ bilan, ODDIY va TABIIY o'zbek tilida "
                "qayta hikoya qilish.\n\n"
                "QATTIQ TAQIQ: yangi, notanish, sun'iy so'z yasamang (masalan "
                "\"hafifvazn\", \"ob'yekt\" kabi so'zlarni umuman ishlatmang - bular "
                "o'zbek tilida yo'q va tushunarsiz). Faqat oddiy odam kundalik "
                "hayotda ishlatadigan, gazeta/sport sharhida tanish so'zlardan "
                "foydalaning.\n\n"
                "To'g'ri atamalar namunasi:\n"
                "- lightweight -> \"yengil vazn toifasi\"\n"
                "- favorite/favored -> \"g'olib sifatida ko'rilmoqda\" yoki "
                "\"kuchliroq deb hisoblanmoqda\"\n"
                "- odds -> \"stavkalar\" yoki \"g'alaba ehtimoli\"\n"
                "- title fight/co-main event -> \"asosiy jang\", \"ikkinchi asosiy jang\"\n\n"
                "MISOL:\n"
                "Inglizcha: \"Benoit Saint Denis remains a narrow favorite over Paddy "
                "Pimblett heading into their UFC 329 lightweight co-main event, though "
                "the betting line has tightened.\"\n"
                "NOTO'G'RI (sun'iy, tushunarsiz): \"Benoit Saint Denis va Paddy "
                "Pimblett o'rtasidagi jangda Saint Denis hali ham kichik foydasiga ega "
                "bo'lsa-da, stavkalar birga yaqinlashib bormoqda. Ular hafifvazn "
                "ob'yektidagi asosiy bahsning yonida jang qiladi.\"\n"
                "TO'G'RI (tabiiy, tushunarli): \"UFC 329 turnirining yengil vazn "
                "toifasidagi jangida Benoit Saint Denis hali ham Paddy Pimblettdan "
                "biroz kuchliroq deb topilmoqda, biroq ikkalasining imkoniyati "
                "tobora tenglashib bormoqda.\"\n\n"
                "Boshqa qoidalar:\n"
                "- Inglizcha jumla tuzilishini ko'chirmang. Avval matnni to'liq "
                "tushuning, keyin xuddi shu voqeani boshidan o'zbekcha gapirib "
                "bering.\n"
                "- Bahouvchilar ismini, tashkilot nomlarini (UFC, PFL, Bellator, ONE "
                "Championship) o'zgartirmang yoki tarjima qilmang.\n"
                "- Raqamlar, sanalar, faktlarni aniq saqlang.\n"
                "- Summary uzun bo'lmasin - 2-3 qisqa, tushunarli jumla yetarli. Har "
                "bir so'zni o'qigan odam birinchi marta o'qishdayoq tushunishi kerak.\n\n"
                'Faqat shu JSON formatida javob bering, boshqa hech qanday matn yozmang: '
                '{"title": "qisqa, tushunarli sarlavha", "summary": "oddiy tilda qayta hikoya qilingan xulosa"}'
            ),
            messages=[{
                "role": "user",
                "content": f"Sarlavha: {title}\n\nMatn: {summary}"
            }]
        )
        raw = response.content[0].text.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(raw)
        return {
            "title": parsed.get("title") or title,
            "summary": parsed.get("summary") or summary,
        }
    except Exception as e:
        print(f"OGOHLANTIRISH: tarjima xatosi - {e}")
        return {"title": title, "summary": summary}
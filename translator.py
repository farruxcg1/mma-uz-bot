import json

from anthropic import AsyncAnthropic

from config import ANTHROPIC_API_KEY

client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
AI_MODEL = "claude-haiku-4-5-20251001"


async def translate_to_uzbek(title: str, summary: str) -> dict:
    """
    Ingliz tilidagi MMA yangiligi sarlavhasi va qisqacha matnini o'zbek tiliga,
    sport jurnalistikasiga xos jonli uslubda tarjima qiladi.

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
                "Siz sport jurnalisti sifatida ingliz tilidagi MMA/UFC yangiliklarini "
                "o'zbek tiliga tabiiy, qisqa va tushunarli tilda tarjima qilasiz.\n\n"
                "Qoidalar:\n"
                "- Bahouvchilar ismini, tashkilot nomlarini (UFC, PFL, Bellator, ONE "
                "Championship) o'zgartirmang yoki tarjima qilmang.\n"
                "- Haddan tashqari rasmiy emas, sport sharhlovchisiga xos jonli, qiziqarli "
                "uslubda yozing.\n"
                "- Summary uzun bo'lmasin - 2-3 jumla yetarli.\n\n"
                'Faqat shu JSON formatida javob bering, boshqa hech qanday matn yozmang: '
                '{"title": "tarjima qilingan sarlavha", "summary": "qisqa tarjima qilingan xulosa"}'
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

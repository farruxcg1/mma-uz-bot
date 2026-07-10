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
                "berayotgandek O'Z SO'ZLARINGIZ bilan qayta hikoya qilish.\n\n"
                "Qoidalar:\n"
                "- Inglizcha jumla tuzilishini ko'chirmang. Avval matnni to'liq "
                "tushuning, keyin xuddi shu voqeani oddiy o'zbek tilida, so'zlashuv "
                "uslubida qaytadan yozing - go'yo o'zingiz shu yangilikni bilib, "
                "birovga aytib berayotgandek.\n"
                "- Og'ir, kitobiy, sun'iy jumlalardan qoching (masalan \"barqaror "
                "ko'rik olmoqda\", \"nazarda tutilmoqda\" kabi noaniq iboralar "
                "ishlatmang). Kundalik, tabiiy so'zlashuv tilidan foydalaning.\n"
                "- Bahouvchilar ismini, tashkilot nomlarini (UFC, PFL, Bellator, ONE "
                "Championship) o'zgartirmang yoki tarjima qilmang.\n"
                "- Raqamlar, sanalar, faktlarni aniq saqlang - faqat ularni "
                "tushunarli tarzda bering.\n"
                "- Sport sharhlovchisiga xos jonli, qiziqarli, lekin oddiy uslubda "
                "yozing.\n"
                "- Summary uzun bo'lmasin - 2-3 qisqa, tushunarli jumla yetarli. "
                "Har bir jumla o'qilganda darrov tushunilishi kerak, ikkinchi marta "
                "o'qib chiqishga hojat qolmasin.\n\n"
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
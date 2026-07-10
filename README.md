# MMA UZ Bot

MMA/UFC olamidan tezkor yangiliklarni ingliz tilidagi manbalardan olib, Claude AI
orqali o'zbek tiliga tarjima qilib, Telegram kanalga avtomatik joylab turuvchi bot.

## Qanday ishlaydi

1. Har **20 daqiqada** (sozlanadi) uchta manbani tekshiradi: **Sherdog**, **BJ Penn**, **LowKick MMA**
2. Yangi maqola topilsa - sarlavha va qisqacha matnni Claude API orqali o'zbek tiliga tarjima qiladi
3. Tarjima qilingan xabarni belgilangan Telegram kanalga yuboradi
4. Bazada saqlaydi - bir xil maqola ikki marta yuborilmaydi
5. **Birinchi ishga tushishda** hozirgi feedlardagi eski maqolalarni "spam" qilib yubormaydi - faqat belgilab qo'yadi, shundan keyingi haqiqiy YANGI maqolalarni e'lon qiladi

## 1-qadam: Bot yaratish

1. Telegram'da [@BotFather](https://t.me/BotFather) bilan gaplashing
2. `/newbot` yuboring, nom va username bering
3. Sizga beriladigan **tokenni** saqlab qo'ying — bu `BOT_TOKEN`

## 2-qadam: Kanal yaratish

1. Telegram'da yangi kanal oching (Public yoki Private — ikkalasi ham ishlaydi)
2. Kanal sozlamalari → **Administrators** → yuqorida yaratgan botingizni admin qilib qo'shing (kamida "Post Messages" huquqi bilan)
3. Kanal **username**'ini eslab qoling (masalan `@mma_uz_kanal`) — bu `CHANNEL_ID`.
   Agar kanal **Private** bo'lsa, username o'rniga raqamli ID kerak bo'ladi (masalan `-1001234567890`) — buni [@userinfobot](https://t.me/userinfobot) yordamida yoki kanaldan botga forward qilingan xabar orqali topish mumkin.

## 3-qadam: O'z Telegram ID'ingizni bilib olish

`/status` va `/check` buyruqlari faqat adminlar uchun. O'z ID'ingizni [@userinfobot](https://t.me/userinfobot) orqali biling — bu `ADMIN_IDS`.

## 4-qadam: Railway'da joylashtirish

1. [railway.app](https://railway.app) da yangi loyiha oching
2. **+ New** → **Database** → **PostgreSQL** qo'shing (Kontakt Plus'dagi kabi)
3. **+ New** → **GitHub Repo** → shu loyihani push qilgan repo'ingizni tanlang
4. Loyiha **Variables** bo'limida quyidagilarni kiriting:
   - `BOT_TOKEN` — 1-qadamdagi token
   - `CHANNEL_ID` — 2-qadamdagi kanal
   - `DATABASE_URL` — PostgreSQL xizmati avtomatik beradi (`${{Postgres.DATABASE_URL}}` deb yozib bog'lash mumkin)
   - `ANTHROPIC_API_KEY` — Kontakt Plus'da ishlatilgan Claude API kaliti
   - `ADMIN_IDS` — 3-qadamdagi ID
   - `POLL_INTERVAL_MINUTES` — ixtiyoriy, standart 20
5. **Deploy** tugmasini bosing

## Mahalliy sinov (kompyuteringizda)

```bash
pip install -r requirements.txt
cp .env.example .env
# .env faylini o'zingizning ma'lumotlaringiz bilan to'ldiring
python main.py
```

## Buyruqlar (faqat ADMIN_IDS uchun)

- `/status` — bot holati, jami e'lon qilingan maqolalar soni
- `/check` — navbatdagi tekshirishni kutmasdan, darhol majburiy tekshirish

## Yangi manba qo'shish

`feeds.py` faylini oching, ro'yxatga yangi dict qo'shing:

```python
{"name": "Manba nomi", "url": "https://manba.com/rss-yoki-feed-manzili"},
```

Boshqa hech narsani o'zgartirish shart emas.

## Eslatma

- RSS manbalar vaqti-vaqti bilan formatini o'zgartirishi yoki vaqtincha ishlamay qolishi mumkin — bot bitta manba xato bersa, boshqalarini tekshirishda davom etadi (to'xtab qolmaydi)
- Agar `ANTHROPIC_API_KEY` berilmasa, bot ishlashda davom etadi, lekin yangiliklar original ingliz tilida e'lon qilinadi

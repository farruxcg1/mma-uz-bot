import os
from dotenv import load_dotenv

# .env faylidagi o'zgaruvchilarni yuklaymiz
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
# Kanal ID yoki username, masalan: @mma_uz_kanal yoki -1001234567890
CHANNEL_ID = os.getenv("CHANNEL_ID")

DATABASE_URL = os.getenv("DATABASE_URL")

# Tarjima uchun - agar bo'lmasa, tarjimasiz (original ingliz tilida) e'lon qilinadi
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# /status va /check buyruqlariga faqat shu ID'lar kira oladi
ADMIN_IDS = [
    int(admin_id.strip())
    for admin_id in os.getenv("ADMIN_IDS", "").split(",")
    if admin_id.strip()
]

# Necha daqiqada bir marta yangi yangilik borligini tekshirsin
POLL_INTERVAL_MINUTES = int(os.getenv("POLL_INTERVAL_MINUTES", "20"))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi! .env faylini tekshiring.")

if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID topilmadi! .env faylini tekshiring.")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL topilmadi! .env faylini tekshiring.")

if ANTHROPIC_API_KEY:
    print(f"INFO: ANTHROPIC_API_KEY topildi (boshi: {ANTHROPIC_API_KEY[:12]}...)")
else:
    print("OGOHLANTIRISH: ANTHROPIC_API_KEY topilmadi - yangiliklar tarjimasiz (original ingliz tilida) e'lon qilinadi.")

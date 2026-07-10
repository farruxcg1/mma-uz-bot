from datetime import datetime

from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import DATABASE_URL


class Base(DeclarativeBase):
    pass


class PostedArticle(Base):
    """
    Kanalga allaqachon yuborilgan (yoki bootstrap bosqichida ko'rilgan deb
    belgilangan) yangiliklar. `guid` orqali bir xil maqola ikki marta
    yuborilishining oldi olinadi.
    """
    __tablename__ = "posted_articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(50))
    guid: Mapped[str] = mapped_column(Text, unique=True, index=True)
    title: Mapped[str] = mapped_column(Text)
    posted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# Railway odatda "postgresql://" beradi, asyncpg uchun "postgresql+asyncpg://" kerak
_async_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(_async_url)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    """Bot birinchi marta ishga tushganda kerakli jadvalni yaratadi (agar hali yo'q bo'lsa)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

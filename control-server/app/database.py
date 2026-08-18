from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from sqlalchemy.orm import DeclarativeBase

from config import DATABASE_URL


# =========================
# Base Model
# =========================

class Base(DeclarativeBase):
    pass


# =========================
# Database Engine
# =========================

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)


# =========================
# Async Session Factory
# =========================

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# =========================
# FastAPI Dependency
# =========================

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# =========================
# Create Tables
# =========================

async def init_db():

    from models import Base

    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )


# =========================
# Shutdown
# =========================

async def close_db():

    await engine.dispose()

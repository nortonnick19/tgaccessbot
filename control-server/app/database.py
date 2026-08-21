import logging

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)

from sqlalchemy.orm import DeclarativeBase

from config import DATABASE_URL



logger = logging.getLogger(
    "database"
)



# =====================================================
# DATABASE ENGINE
# =====================================================

engine = create_async_engine(

    DATABASE_URL,

    echo=False,


    # Проверка живости соединения
    pool_pre_ping=True,


    # Количество постоянных соединений
    pool_size=10,


    # Дополнительные соединения при нагрузке
    max_overflow=20,


    # Таймаут ожидания соединения
    pool_timeout=30,


    # Перезапуск соединений через час
    pool_recycle=3600

)





# =====================================================
# SESSION
# =====================================================

async_session = async_sessionmaker(

    bind=engine,

    class_=AsyncSession,


    # Важно для async SQLAlchemy
    # чтобы объекты не теряли данные после commit

    expire_on_commit=False,


    # строгий режим
    autoflush=False

)





# =====================================================
# BASE MODEL
# =====================================================

class Base(
    DeclarativeBase
):
    pass






# =====================================================
# INIT DATABASE
# =====================================================

async def init_db():


    from models import Base



    logger.info(
        "Initializing database"
    )



    async with engine.begin() as conn:


        await conn.run_sync(

            Base.metadata.create_all

        )



    logger.info(
        "Database initialized"
    )







# =====================================================
# CLOSE DATABASE
# =====================================================

async def close_db():


    logger.info(
        "Closing database"
    )


    await engine.dispose()


    logger.info(
        "Database closed"
    )

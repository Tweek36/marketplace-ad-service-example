import asyncio
import os

import asyncpg
from asyncpg import Connection


async def get_db_connection() -> Connection:
    """Создать соединение с базой данных."""
    conn_string = os.getenv(
        "POSTGRES_CONNECTION_STRING",
        "postgres://postgres:postgres@ad-postgres:5432/ads_db",
    )
    return await asyncpg.connect(conn_string)


async def clean_database(conn: Connection) -> None:
    """Очистить базу данных от лишних записей."""
    print("Начинаю очистку базы данных...")

    # Удаляем записи из outbox, связанные с объявлениями id > 10
    outbox_query = """
    DELETE FROM outbox
    WHERE CAST(payload->>'ad_id' AS INTEGER) > 10
    """
    result = await conn.execute(outbox_query)
    print(f"Удалено {result.split()[-1]} записей из outbox")

    # Удаляем объявления с id > 10
    ads_query = """
    DELETE FROM ads
    WHERE id > 10
    """
    result = await conn.execute(ads_query)
    print(f"Удалено {result.split()[-1]} объявлений из ads")


async def main() -> None:
    """Основная функция."""
    try:
        conn = await get_db_connection()
        try:
            await clean_database(conn)
            print("Очистка базы данных завершена успешно!")
        finally:
            await conn.close()
    except Exception as e:
        print(f"Ошибка при очистке базы данных: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

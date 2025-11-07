import psycopg2
from settings import db_conf


def test_connection():
    conn = psycopg2.connect(**db_conf)

    print('✓ Подключение успешно!')

    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    print(f"Версия PostgreSQL: {cursor.fetchone()[0]}")

    cursor.close()
    return True


if __name__ == '__main__':
    test_connection()

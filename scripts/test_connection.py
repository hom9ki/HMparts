import psycopg2
from settings import db_conf


def test_connection():
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'user': 'xomma',
        'password': 'nokia920',
        'database': 'postgres'
    }
    print(db_conf)
    print(db_config)
    conn = psycopg2.connect(**db_config)

    print('✓ Подключение успешно!')

    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    print(f"Версия PostgreSQL: {cursor.fetchone()[0]}")

    cursor.close()
    return True


if __name__ == '__main__':
    test_connection()

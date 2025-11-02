import psycopg2


def test_connection():
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        user='xomma',
        password='nokia920',
        database='education'
    )

    print('✓ Подключение успешно!')

    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    print(f"Версия PostgreSQL: {cursor.fetchone()[0]}")

    cursor.close()
    return True


if __name__ == '__main__':
    test_connection()

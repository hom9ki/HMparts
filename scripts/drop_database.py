import psycopg2
import sys
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def drop_db():
    db_conf = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': 'nokia920',
        'database': 'postgres'
    }
    try:
        connection = psycopg2.connect(**db_conf)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        print('Подключение установлено успешно')

        cursor.execute("DROP DATABASE education;")
        exist_db = cursor.fetchone()
        if not exist_db:
            print('База данных "education" успешно удалена')

        cursor.close()
        connection.close()

    except Exception as e:
        print(f'Не удалось БД: {e}')

if __name__ == '__main__':
    drop_db()
import psycopg2
import sys
import os
from settings import db_conf
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_database():
    print('Подключение к БД...')

    db_config = db_conf.copy()
    db_config['database'] = 'postgres'
    print(db_config)

    connection = psycopg2.connect(**db_config)
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    print('Подключение установлено успешно')

    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_conf['database'],))
    exists_db = cursor.fetchone()
    if exists_db:
        print(f'База данных {db_conf['database']} уже существует')

    else:
        cursor.execute(f"CREATE DATABASE {db_conf['database']}")
        print(f'База данных "{db_conf['database']}" создана')

    cursor.close()
    connection.close()


def create_user_if_not_exists():
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': 'nokia920',
        'database': 'postgres'
    }

    try:
        connection = psycopg2.connect(**db_config)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()

        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (db_conf['user'],))
        exists_user = cursor.fetchone()

        if not exists_user:
            cursor.execute(f"CREATE USER {db_conf['user']} WITH PASSWORD %s", (db_conf['password'],))
            cursor.execute("""
                SELECT rolcreatedb as can_create_db FROM pg_roles WHERE rolname = %s""", (db_conf['user'],))
            print('Пользователь "xomma" создан')
            if not cursor.fetchone()[0]:
                cursor.execute(f"ALTER USER {db_conf['user']} WITH CREATEDB")
                print(f'Пользователю {db_conf["user"]} выдано право CREATEDB')
        else:
            cursor.execute(f"ALTER USER {db_conf['user']} WITH CREATEDB")
            print(f'Пользователю {db_conf["user"]} выдано право CREATEDB')

            cursor.close()
            connection.close()
    except Exception as e:
        print(f'Не удалось создать пользователя: {e}')


def test_connection():
    print(f'Проверка подключения к БД {db_conf['database']}')

    conn = psycopg2.connect(**db_conf)

    print('✓ Подключение успешно!')

    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    print(f"Версия PostgreSQL: {cursor.fetchone()[0]}")
    print(f'\nhost: {db_conf["host"]}\nport: {db_conf["port"]}\nuser: {db_conf["user"]}\ndatabase: {db_conf["database"]}')

    cursor.close()
    return True


if __name__ == '__main__':
    create_user_if_not_exists()
    create_database()
    test_connection()

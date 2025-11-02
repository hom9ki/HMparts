import psycopg2
import sys
import os

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_database():
    db_conf = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': 'nokia920',
        'database': 'postgres'
    }

    connection = psycopg2.connect(**db_conf)
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    print('Подключение установлено успешно')

    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'education'")
    exists_db = cursor.fetchone()
    if exists_db:
        print('База данных "education" уже существует')
    else:
        cursor.execute("CREATE DATABASE education")
        print('База данных "education" создана')

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

        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'xomma'")
        exists_user = cursor.fetchone()

        if not exists_user:
            cursor.execute("CREATE USER xomma WITH PASSWORD 'nokia920'")
            print('Пользователь "xomma" создан')

        cursor.execute("GRANT ALL PRIVILEGES ON DATABASE education TO xomma")
        print('Права на базу данных "education" выданы пользователю "xomma"')

        cursor.close()
        connection.close()
    except Exception as e:
        print(f'Не удалось создать пользователя: {e}')


def grant_shema_priviliges():
    db_cofig = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': 'nokia920',
        'database': 'education'
    }

    connection = psycopg2.connect(**db_cofig)
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()

    cursor.execute("GRANT ALL ON SCHEMA public TO xomma")
    print('Права на схему "public" выданы пользователю "xomma"')

    cursor.execute("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO xomma")


if __name__ == '__main__':
    create_database()
    create_user_if_not_exists()
    grant_shema_priviliges()

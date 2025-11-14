import os
import subprocess
import sys


def run_init_db():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_dir)
    print(project_dir)

    scripts = [
        'scripts/test_encoding.py',
        ['manage.py', 'migrate'],
        'scripts/init_dump.py',
    ]

    for script in scripts:
        if isinstance(script, list):
            subprocess.run([sys.executable] + script, check=True)
            print(f'Успешно: {" ".join(script)}')
        elif isinstance(script, str):
            if not os.path.exists(script):
                print(f'Скрипт не найден: {script}')
                continue
            else:
                subprocess.run([sys.executable, script], check=True)
                print(f'Успешно: {script}')

    print('БД и данные успешно инициализированы')


if __name__ == '__main__':
    run_init_db()

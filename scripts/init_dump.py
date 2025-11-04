import os
import subprocess


def init_dump():
    dumps = ['users', 'garage', 'product', 'cart', 'feedback']
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_dir)

    for dump in dumps:
        print(f'Рабочая директория{os.getcwd()}')
        print(f'Директория проекта {project_dir}')
        path = f'fixtures/{dump}_data.json'

        cmd = ['python', 'manage.py', 'loaddata', path]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f'Dump {dump} загружен.')


if __name__ == '__main__':
    init_dump()

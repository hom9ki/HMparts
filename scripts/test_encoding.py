import os
import chardet

dumps_list = ['users', 'product', 'garage', 'feedback', 'cart']


def fix_encoding(dump):
    try:
        dump_path = f"../fixtures/{dump}_data.json"

        if not os.path.exists(dump_path):
            print("Файл не найден")
            return False
        with open(dump_path, 'rb') as f:
            raw_data = f.read()
            encoding = chardet.detect(raw_data)['encoding']
            print(f'Обнаружена кодировка: {encoding}')

        with open(dump_path, 'r', encoding=encoding) as f:
            content = f.read()

        with open(dump_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Файл {dump}_data.json успешно перекодирован")
        return True
    except Exception as e:
        print(f"Ошибка при перекодировании: {e}")
        return False


if __name__ == '__main__':
    for dump in dumps_list:
        fix_encoding(dump)

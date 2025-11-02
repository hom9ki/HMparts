import os
import yadisk
from django.conf import settings

def upload_recurcive(ya, remote_path, local_path):

    for item_name in os.listdir(local_path):
        if item_name == '.gitkeep':
            continue

        local_item_path = os.path.join(local_path, item_name)
        remote_item_path = f'{remote_path}/{item_name}'

        if os.path.isdir(local_item_path):
            if not ya.exists(remote_item_path):
                ya.makedirs(remote_item_path)

            upload_recurcive(ya, remote_item_path, local_item_path)
            print(f'Загружена папка: {item_name}')
        else:
            ya.upload(local_item_path, remote_item_path)
            print(f'Загружен файл: {item_name}')


def upload_media():
    TOKEN = 'a1c953cfaffb471b916da5b545055d4c'
    REMOTE_MEDIA_PATH = '/HMparts_media'
    LOCAL_MEDIA_PATH = settings.MEDIA_ROOT

    try:
        ya = yadisk.YaDisk(token=TOKEN)
        if not ya.check_token():
            print('Неверный токен Яндекс.Диска')
            return False

        print('Подключение к Яндекс.Диску установлено')

        if not ya.exists(REMOTE_MEDIA_PATH):
            ya.makedirs(REMOTE_MEDIA_PATH)
            print(f' Создана удаленная папка: {REMOTE_MEDIA_PATH}')

        upload_recurcive(ya, REMOTE_MEDIA_PATH, LOCAL_MEDIA_PATH)

        print('Медиафайлы успешно загружены на Яндекс.Диск')
        return True

    except Exception as e:
        print(f'Ошибка при скачивании: {e}')
        return False

if __name__ == '__main__':
    upload_media()
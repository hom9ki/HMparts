import os
import yadisk
from django.conf import settings


def download_recursive(ya, remote_path, local_path):
    for item in ya.listdir(remote_path):
        remote_item_path = item.path
        local_item_path = os.path.join(local_path, item.name)

        if item.type == 'dir':
            os.makedirs(local_item_path, exist_ok=True)
            download_recursive(ya, remote_item_path, local_item_path)
            print('Скачана папка: {item.name}"')
        else:
            ya.download(remote_item_path, local_item_path)
            print('Скачан файл: {item.name}')


def download_media():
    TOKEN = 'y0__xDy68rUARjblgMg-4fl_xRBDTuFF7oXhhaIUdxaNLOLXULbjQ'
    REMOTE_MEDIA_PATH = '/HMparts_media'
    LOCAL_MEDIA_PATH = settings.MEDIA_ROOT

    try:
        ya = yadisk.YaDisk(token=TOKEN)
        if not ya.check_token():
            print('Неверный токен Яндекс.Диска')
            return False
        print('Подключение к Яндекс.Диску установлено')

        if not ya.exists(REMOTE_MEDIA_PATH):
            print(f' Удаленная папка не найдена: {REMOTE_MEDIA_PATH}')
            return False

        os.makedirs(LOCAL_MEDIA_PATH, exist_ok=True)

        download_recursive(ya, REMOTE_MEDIA_PATH, LOCAL_MEDIA_PATH)
        print('Медиафайлы успешно скачаны с Яндекс.Диска')
        return True
    except Exception as e:
        print(f'Ошибка при скачивании: {e}')
        return False


if __name__ == '__main__':
    download_media()

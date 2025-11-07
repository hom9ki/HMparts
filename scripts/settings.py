from app.settings import MEDIA_ROOT, DATABASES


# yandex
TOKEN = 'y0__xDy68rUARjblgMg-4fl_xRBDTuFF7oXhhaIUdxaNLOLXULbjQ'
REMOTE_MEDIA_PATH = '/HMparts_media'
LOCAL_MEDIA_PATH = MEDIA_ROOT

# БД
db_settings = DATABASES['default']
db_conf = {
    'host': db_settings['HOST'],
    'port': db_settings['PORT'],
    'user': db_settings['USER'],
    'password': db_settings['PASSWORD'],
    'database': db_settings['NAME']
}

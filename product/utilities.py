from datetime import datetime
from os.path import splitext





def get_image_filename(instance, filename, folder):
    date = datetime.now().timestamp()
    file_name = splitext(filename)
    result = f'{folder}/{date}{file_name}'
    return result


def get_image_filename_category(instance, filename):
    return get_image_filename(instance, filename, 'category')

def get_image_filename_product(instance, filename):
    return get_image_filename(instance, filename, 'product')

def get_image_filename_set(instance, filename):
    return get_image_filename(instance, filename, 'set')





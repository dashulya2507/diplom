from celery import shared_task
from .services import import_shop_data


@shared_task
def do_import(path='data/shop1.yaml'):
    import_shop_data(path)
    return True

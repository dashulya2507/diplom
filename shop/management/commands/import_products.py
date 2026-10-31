from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from shop.services import import_shop_data


class Command(BaseCommand):
    help = 'Импортирует товары поставщика из YAML-файла или URL.'

    def add_arguments(self, parser):
        parser.add_argument('source', nargs='?', default='data/shop1.yaml')

    def handle(self, *args, **options):
        source = Path(options['source']) if not str(options['source']).startswith(('http://', 'https://')) else options['source']
        try:
            shop = import_shop_data(source)
        except Exception as exc:
            raise CommandError(f'Ошибка импорта: {exc}') from exc
        self.stdout.write(self.style.SUCCESS(f'Импорт завершён: {shop.name}'))

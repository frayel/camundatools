from django.core.management.base import BaseCommand

from core.tasks import wait_seconds


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('seconds', type=int, help='Seconds')

    def handle(self, *args, **options):
        seconds = options.get('seconds', 0)
        self.stdout.write(self.style.HTTP_INFO(f'Comando enviado...'))
        result = wait_seconds.delay(seconds)
        output = result.get(timeout=seconds+1)
        self.stdout.write(self.style.SUCCESS(output))


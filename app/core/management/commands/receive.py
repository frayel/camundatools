from django.core.management.base import BaseCommand
from kafka import KafkaConsumer


class Command(BaseCommand):

    def handle(self, *args, **options):
        consumer = KafkaConsumer('topico_teste', bootstrap_servers='localhost:9092')
        for msg in consumer:
            self.stdout.write(self.style.HTTP_INFO(f'Mensagem Recebida: {msg}'))
        self.stdout.write(self.style.SUCCESS(f'Fim das mensagens.'))


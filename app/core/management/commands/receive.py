from django.core.management.base import BaseCommand
from kafka import KafkaConsumer


class Command(BaseCommand):

    def handle(self, *args, **options):
        consumer = KafkaConsumer(
            'topico_teste',
            #auto_offset_reset='earliest',
            bootstrap_servers='localhost:9092',
            consumer_timeout_ms=1000,
            group_id='grupo.teste')
        for msg in consumer:
            self.stdout.write(self.style.HTTP_INFO(f'Mensagem Recebida: {msg}'))
        consumer.close()
        self.stdout.write(self.style.SUCCESS(f'Fim das mensagens.'))


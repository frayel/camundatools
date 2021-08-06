import json

from django.core.management.base import BaseCommand
from kafka import KafkaProducer


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('mensagem', type=str, help='Mensagem')

    def handle(self, *args, **options):
        mensagem = options.get('mensagem', 'Hello World')
        producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send('topico_teste', {'mensagem': mensagem})
        #self.stdout.write(self.style.HTTP_INFO(f'Comando enviado...'))
        self.stdout.write(self.style.SUCCESS('Comando Enviado.'))


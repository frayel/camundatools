from django.core.management.base import BaseCommand
from apps.webapp.services.camunda_bpm import CamundaBpm
from apps.webapp.services.exceptions import ParametroInvalido
from django.conf import settings
import sys


class Command(BaseCommand):

    help = 'Este script exclui todos os processos ativos de um processo bpm. Somente deve ser executado em ambiente de teste.'

    def handle(self, *args, **options):

        if settings.AMBIENTE != 'DESENVOLVIMENTO' and settings.AMBIENTE != 'TESTE':
            self.stderr.write(self.style.ERROR('Este comando só pode ser executado em ambiente de teste ou desenvolvimento!'))
            sys.exit(1)

        try:
            camunda = CamundaBpm()
            camunda.sigin()

            for definicao in camunda.carregar_definicoes():
                for instancia in camunda.listar_instancias_por_business_key(definicao['key']):
                    camunda.excluir_instancia(instancia['id'], 'Cancelado por comando')
                    self.stdout.write(self.style.SUCCESS(f'Instancia BPMN {instancia["id"]} excluida !'))

            for definicao in camunda.carregar_definicoes_cmmn():
                for instancia in camunda.listar_instancias_cmmn(definicao['key']):
                    camunda.excluir_instancia_cmmn(instancia['id'])
                    self.stdout.write(self.style.SUCCESS(f'Instancia CMMN {instancia["id"]} excluida !'))

        except ParametroInvalido:
            self.stderr.write(self.style.ERROR('Erro !'))
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS(f'Comando Finalizado !'))



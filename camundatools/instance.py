import sys

from django.core.management.base import BaseCommand

from apps.webapp.models.modulo import Modulo
from apps.webapp.services import utils
from apps.webapp.services.camunda_bpm import CamundaBpm
from apps.webapp.services.exceptions import ParametroInvalido


class Command(BaseCommand):

    help = 'Este script realiza a migração para a nova versão dos fluxos bpm instalados.'
    -m all | -k key
    -l
    -cancel id
    -inspect id
    -start key -v vars
    -reset key**


    def handle(self, *args, **options):

        try:
            self.migrate_bpm()

        except ParametroInvalido:
            self.stderr.write(self.style.ERROR('Erro ao migrar fluxos no Camunda!'))
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS(f'Verificação Finalizada!'))

    def migrate_bpm(self):
        self.stdout.write(self.style.HTTP_INFO('Realizando a verificação de versão das definições no Camunda para todos os processos em andamento...'))
        camunda = CamundaBpm()
        camunda.sigin()
        # Para cada Modulo Ativo
        for modulo in Modulo.objects.filter(migra_versao_bpm_automaticamente=True, ativo=True).all():
            ultima_definicao = camunda.obter_ultima_definicao(modulo.process_name)
            # Para cada instância ativa
            for instancia in camunda.listar_instancias_por_business_key(modulo.process_name):
                # Incluir novas variaveis de todos os processos
                variaveis = camunda.obter_variavel_processo(instancia['id'])
                self.verificar_variaveis(instancia['id'], instancia['businessKey'], camunda, modulo, variaveis)
                if ultima_definicao['id'] != instancia['definitionId']:
                    definicao = camunda.carregar_definicoes(instancia['definitionId'])
                    key_list = list()
                    # Para cada atividade desta instância
                    for atividade in camunda.obter_atividades_por_id(id_processo=instancia['id']):
                        nova_atividade = self.obtem_de_para(modulo.process_name, definicao["version"], atividade["taskDefinitionKey"])
                        key_list.append({
                            "sourceActivityIds": [atividade["taskDefinitionKey"]],
                            "targetActivityIds": [nova_atividade],
                        })
                    try:
                        if key_list and len(key_list) > 0:
                            self.stdout.write(self.style.WARNING(f'Realizando a migração automática do processo {modulo.process_name} {instancia["id"]}: {definicao["versionTag"]} ({definicao["version"]}) -> {ultima_definicao["versionTag"]} ({ultima_definicao["version"]})'))
                            camunda.migrar_definicao([instancia['id']], definicao['id'], ultima_definicao['id'], key_list)
                            for k in key_list:
                                self.stdout.write(self.style.HTTP_INFO(f'Migração de {k["sourceActivityIds"]} para {k["targetActivityIds"]} realizada com sucesso!'))
                        else:
                            self.stdout.write(self.style.WARNING(f'Não há atividades para serem migradas no processo {modulo.process_name} {instancia["id"]}'))
                    except ParametroInvalido as p:
                        erro = str(p).split('\n')[2].replace('\t', '') if len(str(p).split('\n')) >= 3 else str(p)
                        self.stdout.write(self.style.ERROR(f'Não foi possível realizar a atualização do processo {modulo.process_name} {instancia["id"]} -> {str(erro)}'))
                        self.stdout.write(self.style.HTTP_INFO(f'Instruções: {key_list}'))
                # else:
                #     self.stdout.write(self.style.HTTP_SUCCESS(f'O processo {modulo.process_name} {instancia["id"]} já está na última versão.'))

                self.update_vars(camunda, modulo.process_name, instancia['id'])

    def obtem_de_para(self, modulo, versao, atividade):
    
        """ Plano de migração de/para """
    
        if modulo == 'cvnd':
            if versao <= 19 and atividade == 'VerificarParecerCVND':
                atividade = ['AssinarParecerCVND']
            elif versao <= 19 and atividade == 'ElaborarParecerSG':
                atividade = 'ElaborarParecerCVND'
            elif versao <= 48 and atividade == 'AnalisarDevolucaoParecerCVND':
                atividade = 'AssinarParecerCVND'
    
        # if modulo == 'edital':
        #     if versao <= 10 and atividade == 'PrestacaoContas':
        #         atividade = ['ContempladaTotalmente']
    
        return atividade

    def update_vars(self, camunda, process_name, process_id):

        if process_name == 'cvnd':

            """ Variaveis obrigatorias para o processo CVND """
            variaveis = camunda.obter_variavel_processo(process_id)
            if 'retornar_para' not in variaveis:
                camunda.modificar_variavel(process_id, 'retornar_para', '["FLUXO"]', 'json')
                self.stdout.write(self.style.WARNING(f'Variavel <retornar_para> incluida no processo {process_id} com valor inicial...'))
            if 'reposicao_automatica' not in variaveis:
                camunda.modificar_variavel(process_id, 'reposicao_automatica', False, 'Boolean')
                self.stdout.write(self.style.WARNING(f'Variavel <reposicao_automatica> incluida no processo {process_id} com valor inicial...'))
            if 'abertura_concurso' not in variaveis:
                camunda.modificar_variavel(process_id, 'abertura_concurso', False, 'Boolean')
                self.stdout.write(self.style.WARNING(f'Variavel <abertura_concurso> incluida no processo {process_id} com valor inicial...'))
            if 'distribuicao_vaga' not in variaveis:
                camunda.modificar_variavel(process_id, 'distribuicao_vaga', False, 'Boolean')
                self.stdout.write(self.style.WARNING(f'Variavel <distribuicao_vaga> incluida no processo {process_id} com valor inicial...'))
            if 'nao_desanota' not in variaveis:
                camunda.modificar_variavel(process_id, 'nao_desanota', False, 'Boolean')
                self.stdout.write(self.style.WARNING(f'Variavel <nao_desanota> incluida no processo {process_id} com valor inicial...'))
            if 'motivo_devolucao' not in variaveis:
                camunda.modificar_variavel(process_id, 'motivo_devolucao', '', 'String')
                self.stdout.write(self.style.WARNING(f'Variavel <motivo_devolucao> incluida no processo {process_id} com valor inicial...'))

        elif process_name == 'edital':
            """ Variaveis obrigatorias para o processo Edital """
            variaveis = camunda.obter_variavel_processo(process_id)
            if 'interesse ' not in variaveis:
                camunda.modificar_variavel(process_id, 'interesse', 'nao', 'String')
                self.stdout.write(self.style.WARNING(f'Variavel <interesse> incluida no processo {process_id} com valor inicial...'))
            if 'data_encerramento_proposta' not in variaveis:
                camunda.modificar_variavel(process_id, 'data_encerramento_proposta', '2199-12-31T23:59:59', 'String')
                self.stdout.write(self.style.WARNING(
                    f'Variavel <data_encerramento_proposta> incluida no processo {process_id} com valor inicial...'))
            if 'data_relatorio_proposta' not in variaveis:
                camunda.modificar_variavel(process_id, 'data_relatorio_proposta', '2199-12-31T23:59:59', 'String')
                self.stdout.write(self.style.WARNING(
                    f'Variavel <data_relatorio_proposta> incluida no processo {process_id} com valor inicial...'))

        elif process_name == 'sicd':
    
            """ Variaveis obrigatorias para o processo SICD """
            pass

    def verificar_variaveis(self, process_id, business_key, camunda, modulo, variaveis):
        if 'read-from:' not in modulo.model_name:
            model = utils.load_model(modulo.app_name, modulo.model_name)
            if model:
                entidade = model.objects.filter(business_key=business_key).first()
                if entidade:
                    if 'solicitante' not in variaveis and hasattr(entidade, 'usuario'):
                        camunda.modificar_variavel(process_id, 'solicitante', entidade.usuario.username, 'String')
                        self.stdout.write(self.style.WARNING(f'Variavel <solicitante> incluida no processo {process_id}...'))
                    if 'unidade' not in variaveis and hasattr(entidade, 'cod_unidade_solicitante'):
                        camunda.modificar_variavel(process_id, 'unidade', entidade.cod_unidade_solicitante, 'String')
                        self.stdout.write(self.style.WARNING(f'Variavel <unidade> incluida no processo {process_id}...'))
                    if 'sigla_unidade' not in variaveis and 'get_sigla_unidade' in dir(entidade):
                        camunda.modificar_variavel(process_id, 'sigla_unidade', entidade.get_sigla_unidade(), 'String')
                        self.stdout.write(self.style.WARNING(f'Variavel <sigla_unidade> incluida no processo {process_id}...'))
                    if 'nro_processo' not in variaveis and hasattr(entidade, 'nro_processo'):
                        camunda.modificar_variavel(process_id, 'nro_processo', entidade.nro_processo, 'String')
                        self.stdout.write(self.style.WARNING(f'Variavel <nro_processo> incluida no processo {process_id}...'))
                    if 'data_cadastro' not in variaveis and (hasattr(entidade, 'created_at') or 'get_data_criacao' in dir(entidade)):
                        created_at = entidade.get_data_criacao() if hasattr(entidade, 'get_data_criacao') else entidade.created_at
                        camunda.modificar_variavel(process_id, 'data_cadastro', created_at.strftime('%Y-%m-%dT%H:%M:%S.000-0300'), 'Date')
                        self.stdout.write(self.style.WARNING(f'Variavel <data_cadastro> incluida no processo {process_id}...'))
                else:
                    self.stdout.write(self.style.ERROR(f'Entidade {modulo.app_name}.{modulo.model_name}={business_key} não localizada.'))
            else:
                self.stdout.write(self.style.ERROR(f'Model {modulo.app_name}.{modulo.model_name} não encontrado.'))
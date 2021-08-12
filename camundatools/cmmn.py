from camundatools.base_rest import BaseRest


class Cmmn(BaseRest):

    base_url: str
    silent: bool
    results_per_page: int

    def __init__(self, url=None, username=None, password=None, config_file="camundatools.cfg", silent=False):
        super().__init__(silent=silent, config_file=config_file)
        self.base_url = url or self.config.get("config", "API_BASE_URL", fallback="http://localhost:8080/engine-rest")
        username = username or self.config.get("config", "AUTH_USERNAME", fallback="demo")
        password = password or self.config.get("config", "AUTH_PASSWORD", fallback="demo")
        self.max_results_per_page = int(self.config.get("config", "MAX_RESULTS_PER_PAGE", fallback=100))
        self.max_results_non_paginated = int(self.config.get("config", "MAX_RESULTS_NON_PAGINATED", fallback=100))
        self.headers_json = self.get_header(username, password, content_json=True)

        self._API_CMMN_LIST_DEFINITION_URL = '/case-definition'
        self._API_CMMN_GET_DEFINITION_URL = '/case-definition/key/{key}'
        self._API_CMMN_GET_XML_URL = '/case-definition/{id}/xml'
        self._API_CMMN_START_PROCESS_URL = '/case-definition/key/{key}/create'
        self._API_CMMN_LIST_INSTANCES_URL = '/case-instance'
        self._API_CMMN_GET_INSTANCE_URL = '/case-instance/{id}'
        self._API_CMMN_GET_HISTORY_URL = '/history/case-instance/{id}'
        self._API_CMMN_GET_VARIABLES_URL = '/case-instance/{id}/variables'
        self._API_CMMN_UPDATE_VARIABLES_URL = '/case-instance/{id}/variables/{varName}'
        self._API_CMMN_LIST_CASE_URL = '/case-execution'
        self._API_CMMN_START_CASE_URL = '/case-execution/{id}/manual-start'
        self._API_CMMN_COMPLETE_CASE_URL = '/case-execution/{id}/complete'
        self._API_CMMN_TERMINATE_CASE_URL = '/case-instance/{id}/terminate'

    def list_case_definition(self, id_definicao=None):
        url = self.base_url + self._API_CMMN_LIST_DEFINITION_URL
        param = '?latestVersion=true'

        if id_definicao is not None:
            url += '/' + id_definicao

        return super().call('get', url + param, self.headers_json)

    def start_case_definition(self, case_key, business_key, variables):

        url = self.base_url + self._API_CMMN_START_PROCESS_URL
        url = url.replace('{key}', case_key)

        data = {
            'businessKey': business_key,
            'variables': variables,
        }
        return super().call('post', url, self.headers_json, data)

    def list_case_instance(self, case_key, business_key=None):
        url = self.base_url + self._API_CMMN_LIST_INSTANCES_URL
        param = '?caseDefinitionKey='+case_key

        if business_key is not None:
            param = param + '&businessKey=' + str(business_key)

        return super().call('get', url + param, self.headers_json)

    def get_case_instance(self, case_id):
        url = self.base_url + self._API_CMMN_GET_INSTANCE_URL
        url = url.replace('{id}', case_id)
        return super().call('get', url, self.headers_json)

    def get_case_instance_history(self, case_id):
        url = self.base_url + self._API_CMMN_GET_HISTORY_URL
        url = url.replace('{id}', case_id)
        return super().call('get', url, self.headers_json)

    def get_case_variables(self, case_id):
        url = self.base_url + self._API_CMMN_GET_VARIABLES_URL
        url = url.replace('{id}', case_id) + '?deserializeValues=false'
        
        return super().call('get', url, self.headers_json, self.headers_json)

    def update_case_variables(self, case_id, nome_variavel, valor, tipo):
        url = self.base_url + self._API_CMMN_UPDATE_VARIABLES_URL
        url = url.replace('{id}', case_id)
        url = url.replace('{varName}', nome_variavel)
        
        dados = {
            'value': valor,
            'type': tipo,
        }

        return super().call('put', url, self.headers_json, dados)

    def list_case_execution(self, case_key, business_key=None):
        url = self.base_url + self._API_CMMN_LIST_CASE_URL
        
        data = {
            'caseDefinitionKey': case_key,
            'active': True,
        }
        if business_key:
            data['businessKey'] = business_key

        return super().call('post', url, self.headers_json, data)

    def start_case_execution(self, execution_id, variables=None):
        url = self.base_url + self._API_CMMN_START_CASE_URL
        url = url.replace('{id}', execution_id)
        
        data = {'variables': variables} if variables else None
        return super().call('post', url, self.headers_json, data)

    def complete_case_execution(self, execution_id, variables=None):
        url = self.base_url + self._API_CMMN_COMPLETE_CASE_URL
        url = url.replace('{id}', execution_id)
        
        data = {'variables': variables} if variables else None
        return super().call('post', url, self.headers_json, data)

    def terminate_case_instance(self, process_instance):
        url = self.base_url + self._API_CMMN_TERMINATE_CASE_URL
        data = {
            'id': process_instance,
        }
        return super().call('post', url, self.headers_json, data)
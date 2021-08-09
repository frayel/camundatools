from camundacmd.api.base_rest import BaseRest


class Instance(BaseRest):

    base_url: str

    def __init__(self, url=None, username=None, password=None):
        super().__init__()
        self.base_url = url or self.config.get("config", "CAMUNDA_API_BASE_URL")
        self._CAMUNDA_API_INICIAR_PROCESSO = '/process-definition/key/{key}/start'
        self._CAMUNDA_API_LISTAR_INSTANCIAS = '/process-instance'
        username = username or self.config.get("config", "CAMUNDA_AUTH_USERNAME")
        password = password or self.config.get("config", "CAMUNDA_AUTH_PASSWORD")
        self.headers = self.get_header_plain(username, password)

    def start_process(self, process_key, business_key, variables):

        # Verifica se ja nao existe um processo com este id
        processos = self.list(process_key, business_key)
        if processos:
            raise Exception(f'Já existe um processo com o id {business_key}')

        url = self.base_url + self._CAMUNDA_API_INICIAR_PROCESSO
        url = url.replace('{key}', process_key)

        data = {
            'businessKey': business_key,
            'variables': variables,
        }
        return super().call('post', url, self.headers, data)

    def list(self, process_key, business_key=None):

        url = self.base_url + self._CAMUNDA_API_LISTAR_INSTANCIAS
        param = '?processDefinitionKey='+process_key

        if business_key is not None:
            param = param + '&businessKey=' + str(business_key)

        return super().call('get', url + param, self.headers)

    def inspect(self):
        pass

    def cancel(self):
        pass

    def migrate(self):
        pass

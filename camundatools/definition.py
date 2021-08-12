import pathlib
from xml.dom import minidom

from camundatools.base_rest import BaseRest


class Definition(BaseRest):

    base_url: str
    silent: bool

    def __init__(self, url=None, username=None, password=None, config_file="camundatools.cfg", silent=False):
        super().__init__(silent=silent, config_file=config_file)
        self.base_url = url or self.config.get("config", "API_BASE_URL", fallback="http://localhost:8080/engine-rest")
        username = username or self.config.get("config", "AUTH_USERNAME", fallback="demo")
        password = password or self.config.get("config", "AUTH_PASSWORD", fallback="demo")
        self.headers_plain = self.get_header(username, password, content_json=False)
        self.headers_json = self.get_header(username, password, content_json=True)

        self._API_CREATE_DEPLOYMENT_URL = '/deployment/create'
        self._API_DEPLOYMENT_URL = '/deployment/{id}'
        self._API_DEFINITIONS_URL = '/process-definition'
        self._API_VERSION_URL = '/version'
        self._API_STARTING_FORM_URL = '/process-definition/key/{key}/form-variables'
        self._API_STARTING_FORM_KEY_URL = '/process-definition/key/{key}/startForm'
        self._API_LIST_IDENTITY_HISTORY_URL = '/history/identity-link-log'
        self._API_GET_XML_URL = '/process-definition/key/{key}/xml'

    def get_camunda_version(self):
        url = self.base_url + self._API_VERSION_URL
        return super().call('get', url, self.headers_json)

    def deploy(self, file_name, changed_only=True):
        url = self.base_url + self._API_CREATE_DEPLOYMENT_URL

        extensao = pathlib.Path(file_name).suffix
        root_element = 'bpmn:process' if extensao == '.bpmn' else 'cmmn:case' if extensao == '.cmmn' else ''
        mydoc = minidom.parse(file_name)
        items = mydoc.getElementsByTagName(root_element)
        deploy_name = items[0].attributes['name'].value
        if 'camunda:versionTag' in items[0].attributes:
            deploy_name = deploy_name + '_' + items[0].attributes['camunda:versionTag'].value

        data = {
            'deployment-name': deploy_name,
            'deploy-changed-only': 'true' if changed_only else 'false',
        }
        files = {
            f'{file_name}': open(file_name, 'r', encoding='utf8').read(),
        }

        return self.call('post', url, self.headers_plain, data=data, files=files)

    def delete(self, deploy_id, cascade=False):
        url = self.base_url + self._API_DEPLOYMENT_URL
        url = url.replace('{id}', deploy_id)

        if cascade:
            url += '?cascade=true'

        return self.call('delete', url, self.headers_json)

    def list(self, key=None, only_latest_version=False):
        url = self.base_url + self._API_DEFINITIONS_URL
        param = "?firstResult=0"

        if key is not None:
            param += f'&key={key}'
        if only_latest_version:
            param += f'&latestVersion=true'

        return self.call('get', url + param, self.headers_json)

    def inspect(self, process_definition_id=None, key=None):
        url = self.base_url + self._API_DEFINITIONS_URL

        if process_definition_id:
            url += f'/{process_definition_id}'
        elif key:
            url += f'/key/{key}'

        return self.call('get', url, self.headers_json)

    def get_starting_form(self, process_key):
        url = self.base_url + self._API_STARTING_FORM_URL
        url = url.replace('{key}', process_key)
        return super().call('get', url, self.headers_json)

    def get_starting_form_key(self, process_key):
        url = self.base_url + self._API_STARTING_FORM_KEY_URL
        url = url.replace('{key}', process_key)
        return super().call('get', url, self.headers_json)

    def list_identity_history(self, process_key, task_id):
        url = self.base_url + self._API_LIST_IDENTITY_HISTORY_URL
        param = '?taskId=' + task_id + '&processDefinitionKey=' + process_key
        return super().call('get', url + param, self.headers_json)

    def get_xml(self, process_key):
        url = self.base_url + self._API_GET_XML_URL
        url = url.replace('{key}', process_key)
        return super().call('get', url, self.headers_json)
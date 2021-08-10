import pathlib
from xml.dom import minidom

from camundatools.base_rest import BaseRest


class Definition(BaseRest):

    base_url: str
    silent: bool

    def __init__(self, url=None, username=None, password=None, config_file="camundatools.cfg", silent=False):
        super().__init__(silent=silent, config_file=config_file)
        self.base_url = url or self.config.get("config", "CAMUNDA_API_BASE_URL")
        username = username or self.config.get("config", "CAMUNDA_AUTH_USERNAME")
        password = password or self.config.get("config", "CAMUNDA_AUTH_PASSWORD")
        self.headers_plain = self.get_header(username, password, content_json=False)
        self.headers_json = self.get_header(username, password, content_json=True)

        self._API_CREATE_DEPLOYMENT_URL = '/deployment/create'
        self._API_DEPLOYMENT_URL = '/deployment/{id}'
        self._API_DEFINITIONS_URL = '/process-definition'

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
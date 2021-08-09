import pathlib
from xml.dom import minidom

from camundatools.api.base_rest import BaseRest


class Deployment(BaseRest):

    base_url: str

    def __init__(self, url=None, username=None, password=None):
        super().__init__()
        self.base_url = url or self.config.get("config", "CAMUNDA_API_BASE_URL")
        self._CAMUNDA_API_DEPLOY_BPMN = '/deployment/create'
        self._CAMUNDA_API_UNDEPLOY_BPMN = '/deployment/{id}'
        self._CAMUNDA_API_LISTAR_DEFINICOES = '/process-definition'
        username = username or self.config.get("config", "CAMUNDA_AUTH_USERNAME")
        password = password or self.config.get("config", "CAMUNDA_AUTH_PASSWORD")
        self.headers = self.get_header_plain(username, password)

    def create(self, file_name, changed_only=True, silent=False):
        url = self.base_url + self._CAMUNDA_API_DEPLOY_BPMN

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

        return self.call('post', url, self.headers, data=data, files=files, silent=silent)

    def delete(self, deploy_id, cascade=False, silent=False):
        url = self.base_url + self._CAMUNDA_API_UNDEPLOY_BPMN
        url = url.replace('{id}', deploy_id)

        if cascade:
            url += '?cascade=true'

        return self.call('delete', url, self.headers, silent=silent)

    def list(self, key=None, only_latest_version=False, silent=False):
        url = self.base_url + self._CAMUNDA_API_LISTAR_DEFINICOES
        param = "?firstResult=0"

        if key is not None:
            param += f'&key={key}'
        if only_latest_version:
            param += f'&latestVersion=true'

        return self.call('get', url + param, self.headers, silent=silent)

from camundacmd.api.base_rest import BaseRest


class Deployment(BaseRest):

    url: str
    username: str
    password: str

    def __init__(self, url, username, password):
        self.base_url = url
        self._CAMUNDA_API_DEPLOY_BPMN = '/deployment/create'
        self._CAMUNDA_API_UNDEPLOY_BPMN = '/deployment/{id}'
        self.username = username
        self.password = password

    def deploy_bpmn(self, name, file, force=False):
        url = self.base_url + self._CAMUNDA_API_DEPLOY_BPMN

        data = {
            'deployment-name': name,
            'deploy-changed-only': 'false' if force else 'true',
        }
        extensao = 'bpmn' if 'bpmn:definitions' in file else 'cmmn' if 'cmmn:definitions' else 'undefined'

        files = {
            f'{name}.{extensao}': file,
        }
        headers = self.get_header_plain(self.username, self.password)
        return super().call('post', url, headers, data=data, files=files)

    def undeploy_bpmn(self, deploy_id, cascade=False):
        url = self.base_url + self._CAMUNDA_API_UNDEPLOY_BPMN
        url = url.replace('{id}', deploy_id)

        if cascade:
            url += '?cascade=true'

        headers = self.get_header(self.username, self.password)
        return super().call('delete', url, headers)
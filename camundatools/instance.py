from camundatools.base_rest import BaseRest


class Instance(BaseRest):

    base_url: str
    silent: bool

    def __init__(self, url=None, username=None, password=None, config_file="camundatools.cfg", silent=False):
        super().__init__(silent=silent, config_file=config_file)
        self.base_url = url or self.config.get("config", "CAMUNDA_API_BASE_URL")
        username = username or self.config.get("config", "CAMUNDA_AUTH_USERNAME")
        password = password or self.config.get("config", "CAMUNDA_AUTH_PASSWORD")
        self.headers_json = self.get_header(username, password, content_json=True)

        self._API_START_DEFINITIONS_URL = '/process-definition/key/{key}/start'
        self._API_PROCESS_INSTANCE_URL = '/process-instance'
        self._API_GET_INSTANCE_URL = '/process-instance/{id}'
        self._API_DELETE_INSTANCE_URL = '/process-instance/delete'
        self._API_MIGRATION_URL = '/migration/execute'
        self._API_MODIFY_INSTANCE_URL = '/process-instance/{id}/modification'

    def start_process(self, process_key, business_key, variables):

        processos = self.list(process_key, business_key)
        if processos:
            raise Exception(f'Business Key {business_key} already in use!')

        url = self.base_url + self._API_START_DEFINITIONS_URL
        url = url.replace('{key}', process_key)

        data = {
            'businessKey': business_key,
            'variables': variables,
        }
        return super().call('post', url, self.headers_json, data)

    def list(self, process_key=None, business_key=None):

        url = self.base_url + self._API_PROCESS_INSTANCE_URL
        param = '?firstResult=0'
        if process_key:
            param += f'&processDefinitionKey={process_key}'
        if process_key:
            param += f'&businessKey={business_key}'

        return super().call('get', url + param, self.headers_json)

    def inspect(self, process_instance_id):
        url = self.base_url + self._API_GET_INSTANCE_URL
        url = url.replace('{id}', process_instance_id)
        return super().call('get', url, self.headers_json)

    def find(self, process_key, business_key):
        process = self.list(process_key, business_key)
        inspect = self.inspect(process[0]["id"]) if process and len(process) > 0 else None
        return inspect

    def delete(self, process_instance_id, reason):

        # try to find
        self.inspect(process_instance_id)

        url = self.base_url + self._API_DELETE_INSTANCE_URL
        data = {
            'processInstanceIds': [process_instance_id],
            'deleteReason': reason,
        }
        return super().call('post', url, self.headers_json, data)

    def migrate(self, process_instance_ids, source_definition_id, target_definition_id, instructions):
        """ instructions example = [{
                        "sourceActivityIds": [SourceTaskId],
                        "targetActivityIds": [DestinationTaskId],
                    }]
        """

        url = self.base_url + self._API_MIGRATION_URL
        data = {
            'processInstanceIds': process_instance_ids,
            'migrationPlan': {
                'sourceProcessDefinitionId': source_definition_id,
                'targetProcessDefinitionId': target_definition_id,
                'instructions': instructions,
                "updateEventTriggers": True,
            },
        }

        return super().call('post', url, self.headers_json, data)

    def modify(self, process_id, instructions):
        url = self.base_url + self._API_MODIFY_INSTANCE_URL
        url = url.replace('{id}', process_id)
        return super().call('post', url, self.headers_json, instructions)
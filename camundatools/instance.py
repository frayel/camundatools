from camundatools.base_rest import BaseRest


class Instance(BaseRest):

    base_url: str
    silent: bool

    def __init__(self, url=None, username=None, password=None, config_file="camundatools.cfg", silent=False):
        super().__init__(silent=silent, config_file=config_file)
        self.base_url = url or self.config.get("config", "API_BASE_URL", fallback="http://localhost:8080/engine-rest")
        username = username or self.config.get("config", "AUTH_USERNAME", fallback="demo")
        password = password or self.config.get("config", "AUTH_PASSWORD", fallback="demo")
        self.headers_json = self.get_header(username, password, content_json=True)

        self._API_START_DEFINITIONS_URL = '/process-definition/key/{key}/start'
        self._API_PROCESS_INSTANCE_URL = '/process-instance'
        self._API_GET_INSTANCE_URL = '/process-instance/{id}'
        self._API_DELETE_INSTANCE_URL = '/process-instance/delete'
        self._API_MIGRATION_URL = '/migration/execute'
        self._API_MODIFY_INSTANCE_URL = '/process-instance/{id}/modification'
        self._API_RESTART_PROCESS_INSTANCE_URL = '/process-definition/{id}/restart'
        self._API_SEND_MESSAGE_URL = '/message'
        self._CAMUNDA_API_OBTER_VARIAVEL_PROCESSO = '/process-instance/{id}/variables'
        self._API_ACTIVITY_HISTORY_URL = '/history/activity-instance'
        self._API_VARIABLE_INSTANCE_URL = '/history/variable-instance'
        self._API_PROCESS_INSTANCE_HISTORY_URL = '/history/process-instance/{id}'
        self._API_UPDATE_VARIABLE_URL = '/process-instance/{id}/variables/{varName}'
        self._API_GET_XML_URL = '/process-definition/{id}/xml'

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

    def restart_process(self, definition_id, process_id, starting_task_name):
        url = self.base_url + self._API_RESTART_PROCESS_INSTANCE_URL
        url = url.replace('{id}', definition_id)
        dados = {
            'processInstanceIds': [process_id],
            'instructions': [
                {
                  "type": "startBeforeActivity",
                  "activityId": starting_task_name
                }
              ],
        }
        return super().call('post', url, self.headers_json, dados)
    
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
    
    def send_process_message(self, message_name, business_key, process_id=None, variables=None):
        url = self.base_url + self._API_SEND_MESSAGE_URL
        dados = {
            'messageName': message_name,
            'businessKey': business_key,
            'processInstanceId': process_id,
            'processVariables': variables,
        }
        return super().call('post', url, self.headers_json, dados)   

    def get_process_variables(self, process_id):
        url = self.base_url + self._CAMUNDA_API_OBTER_VARIAVEL_PROCESSO
        url = url.replace('{id}', process_id) + '?deserializeValues=false'
        return super().call('get', url, self.headers_json)

    def list_instance_history(self, process_instance, filter_tasks=None):
        if filter_tasks is None:
            filter_tasks = ['serviceTask', 'userTask', 'startEvent', 'endEvent', 'noneEndEvent']
        url = self.base_url + self._API_ACTIVITY_HISTORY_URL
        param = '?processInstanceId=' + process_instance + '&sortBy=occurrence&sortOrder=desc'
        history = super().call('get', url + param, self.headers_json)
        if filter_tasks:
            history = list(filter(lambda h: h['activityType'] in filter_tasks, history))
            history = sorted(history, key=lambda task: task['startTime'], reverse=True)
        return history

    def get_history_variables(self, process_id, variable=None):
        url = self.base_url + self._API_VARIABLE_INSTANCE_URL
        param = '?processInstanceId=' + process_id

        if variable is not None:
            param = param + '&variableName=' + variable

        ret = super().call('get', url + param, self.headers_json)

        if variable is not None:
            return ret[0]['value'] if ret and len(ret) >= 1 else None

        return ret

    def list_process_instance_history(self, process_id):
        url = self.base_url + self._API_PROCESS_INSTANCE_HISTORY_URL
        url = url.replace('{id}', process_id)
        return super().call('get', url, self.headers_json)

    def list_process_instance_history_by_business_key(self, process_key, business_key):
        """ Pode retornar mais de uma instancia, ja que um business_key pode ter mais de uma execucao
            Ex: Processo Reativado
        """
        url = self.base_url + self._API_PROCESS_INSTANCE_HISTORY_URL
        url = url.replace('/{id}', '')
        
        data = {
            'processDefinitionKey': process_key,
            'processInstanceBusinessKey': business_key,
        }
        return super().call('post', url, self.headers_json, data)
    
    def update_variables(self, process_id, variable_name, value, type):
        url = self.base_url + self._API_UPDATE_VARIABLE_URL
        url = url.replace('{id}', process_id)
        url = url.replace('{varName}', variable_name)
        dados = {
            'value': value,
            'type': type,
        }
        return super().call('put', url, self.headers_json, dados)

    def get_xml(self, process_id):
        url = self.base_url + self._API_GET_XML_URL
        url = url.replace('{id}', process_id)
        return super().call('get', url, self.headers_json)

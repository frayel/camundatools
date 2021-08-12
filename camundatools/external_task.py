from camundatools.base_rest import BaseRest


class ExternalTask(BaseRest):

    base_url: str
    silent: bool
    results_per_page: int
    external_max_tasks: int
    external_task_lock_duration: int
    external_task_retry_timeout: int

    def __init__(self, url=None, username=None, password=None, config_file="camundatools.cfg", silent=False):
        super().__init__(silent=silent, config_file=config_file)
        self.base_url = url or self.config.get("config", "API_BASE_URL", fallback="http://localhost:8080/engine-rest")
        username = username or self.config.get("config", "AUTH_USERNAME", fallback="demo")
        password = password or self.config.get("config", "AUTH_PASSWORD", fallback="demo")
        self.external_max_tasks = int(self.config.get("config", "EXTERNAL_MAX_TASKS", fallback=10))
        self.external_task_lock_duration = int(self.config.get("config", "EXTERNAL_TASK_LOCK_DURATION_IN_MILISECONDS", fallback=30000))
        self.external_task_retry_timeout = int(self.config.get("config", "EXTERNAL_TASK_RETRY_TIMEOUT", fallback=300000))
        self.header_json = self.get_header(username, password, content_json=True)
        self._API_LIST_EXTERNAL_TASK_URL = '/external-task'
        self._API_FETCH_EXTERNAL_TASK_URL = '/external-task/fetchAndLock'
        self._API_COMPLETE_EXTERNAL_TASK_URL = '/external-task/{id}/complete'
        self._API_UNLOCK_EXTERNAL_TASK_URL = '/external-task/{id}/unlock'
        self._API_EXTERNAL_TASK_FAILURE_URL = '/external-task/{id}/failure'
        self._API_LIST_INCIDENTS_URL = '/incident'
        self._API_RESOLVE_INCIDENT_URL = '/incident/{id}'
        self._API_SET_RETRIES_URL = '/external-task/{id}/retries'

    def fetch_and_lock_external_tasks(self, process_key, worker_id, topic_name, process_variables=None, business_key=None):
        url = self.base_url + self._API_FETCH_EXTERNAL_TASK_URL
        data = {
            'workerId': worker_id,
            'maxTasks': self.external_max_tasks,
            'topics': [{
                'processDefinitionKey': process_key,
                'topicName': topic_name,
                'lockDuration': self.external_task_lock_duration,
            }]
        }
        if process_variables:
            data['topics'][0]['processVariables'] = process_variables
        if business_key is not None:
            data['topics'][0]['businessKey'] = business_key

        return super().call('post', url, self.header_json, data)

    def list_external_tasks(self, process_instance_id=None, process_key=None, not_locked=True, with_retries=False):
        url = self.base_url + self._API_LIST_EXTERNAL_TASK_URL
        data = {}
        if process_instance_id:
            data['processInstanceId'] = process_instance_id
        if not_locked:
            data['notLocked'] = not_locked
        if with_retries:
            data['withRetriesLeft'] = with_retries

        tasks = super().call('post', url, self.header_json, data)

        if process_key is not None:
            tasks = list(filter(lambda t: t['processDefinitionKey'] == process_key, tasks))

        return tasks

    def complete_external_task(self, task_id, worker_id, variables):
        url = self.base_url + self._API_COMPLETE_EXTERNAL_TASK_URL
        url = url.replace('{id}', task_id)
        data = {
            'workerId': worker_id,
            'variables': variables,
        }
        super().call('post', url, self.header_json, data)
    
    def unlock_external_task(self, external_task_id):
        url = self.base_url + self._API_UNLOCK_EXTERNAL_TASK_URL
        url = url.replace('{id}', external_task_id)
        return super().call('post', url, self.header_json, {})

    def external_task_failure(self, external_task_id, worker_id, mensagem, detalhes, retry):
        url = self.base_url + self._API_EXTERNAL_TASK_FAILURE_URL
        url = url.replace('{id}', external_task_id)
        data = {
            'workerId': worker_id,
            'errorMessage': mensagem,
            'errorDetails': detalhes,
            'retries': retry,
            'retryTimeout': self.external_task_retry_timeout,
        }
        return super().call('post', url, self.header_json, data)

    def list_incidents(self, id_incidente=None, id_processo=None):
        url = self.base_url + self._API_LIST_INCIDENTS_URL
        param = '?sortBy=processDefinitionId&sortOrder=asc'

        if id_incidente is not None:
            param = param + '&incidentId=' + id_incidente
        if id_processo is not None:
            param = param + '&processInstanceId=' + id_processo
        return super().call('get', url + param, self.header_json)

    def resolve_incident(self, id_incidente):
        url = self.base_url + self._API_RESOLVE_INCIDENT_URL
        url = url.replace('{id}', id_incidente)
        return super().call('delete', url, self.header_json)

    def set_retries(self, external_task_id, retries):
        url = self.base_url + self._API_SET_RETRIES_URL
        url = url.replace('{id}', external_task_id)
        data = {
            'retries': retries,
        }
        return super().call('put', url, self.header_json, data)


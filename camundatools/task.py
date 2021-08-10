from camundatools.base_rest import BaseRest


class Task(BaseRest):

    base_url: str
    silent: bool
    results_per_page: int

    def __init__(self, url=None, username=None, password=None, config_file="camundatools.cfg", silent=False):
        super().__init__(silent=silent, config_file=config_file)
        self.base_url = url or self.config.get("config", "CAMUNDA_API_BASE_URL")
        username = username or self.config.get("config", "CAMUNDA_AUTH_USERNAME")
        password = password or self.config.get("config", "CAMUNDA_AUTH_PASSWORD")
        self.max_results_per_page = int(self.config.get("config", "MAX_RESULTS_PER_PAGE"))
        self.max_results_non_paginated = int(self.config.get("config", "MAX_RESULTS_NON_PAGINATED"))
        self.headers_json = self.get_header(username, password, content_json=True)
        self._API_TASK_URL = '/task'
        self._API_COMPLETE_TASK_URL = '/rest/task/{id}/complete'

    def list(self, process_key=None, business_key=None, candidate_groups=None, task_name=None, page=None):
        url = self.base_url + self._API_TASK_URL

        max_results = self.max_results_per_page if page is not None else self.max_results_non_paginated
        first_result = (int(page) - 1) * max_results if page is not None and int(page) > 1 else 0

        param = f'?maxResults=' + str(max_results) \
                + f'&firstResult=' + str(first_result)
        data = {
            'active': True,
            'sortBy': 'created',
            'sortOrder': 'asc',
        }
        if business_key:
            data['processInstanceBusinessKey'] = business_key
        if candidate_groups:
            data['candidateGroups'] = candidate_groups
        if task_name:
            data['taskDefinitionKey'] = task_name
        if process_key:
            data['processDefinitionKeyIn'] = [process_key]

        return super().call('post', url + param, self.headers_json, data)

    def inspect(self, task_id):
        url = self.base_url + self._API_TASK_URL
        param = '/' + str(task_id)
        return super().call('get', url + param, self.headers_json)

    def complete(self, task_id, variables=None):
        url = self.base_url + self._API_COMPLETE_TASK_URL
        url = url.replace('{id}', task_id)
        data = {
            'variables': variables,
        }
        super().call('post', url, self.headers_json, data)

    def delete(self, task_id):
        url = self.base_url + self._API_TASK_URL
        url += f'/{task_id}'
        super().call('delete', url, self.headers_json)


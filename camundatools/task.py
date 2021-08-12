from camundatools.base_rest import BaseRest


class Task(BaseRest):

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

        self._API_TASK_URL = '/task'
        self._API_COMPLETE_TASK_URL = '/task/{id}/complete'
        self._API_CLAIM_TASK_URL = '/task/{id}/claim'
        self._API_UNCLAIM_TASK_URL = '/task/{id}/unclaim'
        self._API_DELEGATE_TASK_URL = '/task/{id}/delegate'
        self._API_UPDATE_TASK_URL = '/task/{id}'
        self.API_TASK_FORM_URL = '/task/{id}/form-variables'
        self._API_LIST_IDENTITY_URL = '/task/{id}/identity-links'

    def list(self, process_key=None, business_key=None, candidate_groups=None, task_name=None,
             query_vars=None, or_queries=None, page=None):
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
        if query_vars:
            data['processVariables'] = query_vars
        if or_queries:
            data['orQueries'] = or_queries

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

    def claim_task(self, task_id, username):
        url = self.base_url + self._API_CLAIM_TASK_URL
        url = url.replace('{id}', task_id)
        data = {
            'userId': username,
        }
        return super().call('post', url, self.headers_json, data)

    def unclaim_task(self, task_id):
        url = self.base_url + self._API_UNCLAIM_TASK_URL
        url = url.replace('{id}', task_id)
        return super().call('post', url, self.headers_json)

    def update_task(self, task_id, dados):
        url = self.base_url + self._API_UPDATE_TASK_URL
        url = url.replace('{id}', task_id)
        return super().call('put', url, self.headers_json, dados)

    def delegate_task(self, task_id, username):
        url = self.base_url + self._API_DELEGATE_TASK_URL
        url = url.replace('{id}', task_id)
        data = {
            'userId': username,
        }
        return super().call('post', url, self.headers_json, data)

    def get_task_form(self, task_id):
        url = self.base_url + self.API_TASK_FORM_URL
        url = url.replace('{id}', task_id)
        return super().call('get', url, self.headers_json)

    def get_identities(self, task_id):
        url = self.base_url + self._API_LIST_IDENTITY_URL
        url = url.replace('{id}', task_id)
        return super().call('get', url, self.headers_json)

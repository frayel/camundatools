import configparser
import datetime
import json
import os
from base64 import b64encode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def datetime_decoder(d):
    if isinstance(d, list):
        pairs = enumerate(d)
    elif isinstance(d, dict):
        pairs = d.items()
    result = []
    for k, v in pairs:
        if isinstance(v, str):
            try:
                v = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%f%z')
            except ValueError:
                try:
                    v = datetime.datetime.strptime(v, '%Y-%m-%d').date()
                except ValueError:
                    pass
        elif isinstance(v, (dict, list)):
            v = datetime_decoder(v)
        result.append((k, v))
    if isinstance(d, list):
        return [x[1] for x in result]
    elif isinstance(d, dict):
        return dict(result)


class BaseRest:

    def __init__(self, silent=False, config_file="camundatools.cfg"):
        if not os.path.isfile(config_file):
            raise Exception(f'File {config_file} does not exist!')
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.silent = silent

    def call(self, method, url, headers, data=None, files=None, binary=False):
        session = requests.Session()
        retries = Retry(total=int(self.config.get('config', 'REQUEST_RETRY', fallback=3)), backoff_factor=1, status_forcelist=[502, 503, 504], allowed_methods=['POST', 'GET', 'PUT', 'PATCH', 'DELETE'])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))
        timeout = int(self.config.get('config', 'REQUEST_TIMEOUT', fallback=5))
        cert_file = self.config.get('config', 'CERT_FILE', fallback=None)

        response = getattr(session, method)(url,
                                            data=json.dumps(data) if files is None else data,
                                            files=files,
                                            headers=headers,
                                            verify=cert_file,
                                            timeout=timeout)

        if not self.silent and response.status_code not in [200, 201, 204, 404]:
            print(f'Server returned an error status.')
            print(f'Request: Url={url} Headers={headers} Data={data}')
            print(f'Response: Status Code={response.status_code} Mensagem={response.content}')

        if response.status_code >= 300:
            mensagem = f'Error Code {response.status_code}'
            if response.content:
                try:
                    error = json.loads(response.content)
                    mensagem = error['message']
                except:
                    mensagem = response.content
            raise Exception(mensagem)
        response.raise_for_status()

        if not binary and response.content != '':
            text = response.content
            try:
                text = json.loads(text, object_hook=datetime_decoder)
            except:
                pass

            return text

        return response.content

    def get_header(self, username, password, content_json=True):
        user_pass = b64encode(f"{username}:{password}".encode()).decode("ascii")
        headers = {'Authorization': f'Basic {user_pass}'}
        if content_json:
            headers['content-type'] = 'application/json'

        return headers
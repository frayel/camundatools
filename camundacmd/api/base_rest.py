import datetime
import json
import logging
from base64 import b64encode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from camundacmd import settings

logger = logging.getLogger(__name__)


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

    @staticmethod
    def call(method, url, headers, data=None, files=None, silent=False, binary=False, extend_timeout=False):
        session = requests.Session()
        retries = Retry(total=settings.REQUEST_RETRY, backoff_factor=1, status_forcelist=[502, 503, 504], allowed_methods=['POST', 'GET', 'PUT', 'PATCH', 'DELETE'])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))
        timeout = settings.REQUEST_TIMEOUT if not extend_timeout else 30

        try:
            if method == 'post' and files is None:
                resposta = session.post(url, data=json.dumps(data), headers=headers, verify=settings.ARQUIVO_CERTIFICADO, timeout=timeout)
            elif method == 'post' and files is not None:
                resposta = session.post(url, data=data, files=files, headers=headers, verify=settings.ARQUIVO_CERTIFICADO, timeout=timeout)
            elif method == 'put':
                resposta = session.put(url, data=json.dumps(data), headers=headers, verify=settings.ARQUIVO_CERTIFICADO, timeout=timeout)
            elif method == 'patch':
                resposta = session.patch(url, data=json.dumps(data), headers=headers, verify=settings.ARQUIVO_CERTIFICADO, timeout=timeout)
            elif method == 'delete':
                resposta = session.delete(url, data=json.dumps(data), headers=headers, verify=settings.ARQUIVO_CERTIFICADO, timeout=timeout)
            elif method == 'get':
                resposta = session.get(url, headers=headers, verify=settings.ARQUIVO_CERTIFICADO, timeout=timeout)
            else:
                raise Exception('Método não implementado')
        except ConnectionError:
            logger.critical('Erro de comunicação', exc_info=True)
            raise Exception('Erro de comunicação')
        except Exception:
            logger.critical('Erro ao executar a chamada remota', exc_info=True)
            raise Exception('Erro ao executar a chamada remota')

        if not silent and resposta.status_code not in [200, 201, 204, 404]:
            logger.error(f'Resposta Inválida do Servidor!')
            logger.error(f'Request: Url={url} Headers={headers} Data={data}')
            logger.error(f'Response: Status Code={resposta.status_code} Mensagem={resposta.content}')

        if resposta.status_code >= 300:
            mensagem = f'Erro {resposta.status_code}'
            if resposta.content:
                try:
                    error = json.loads(resposta.content)
                    mensagem = error['message']
                except:
                    mensagem = resposta.content
            raise Exception(mensagem)
        resposta.raise_for_status()

        if not binary and resposta.content != '':
            text = resposta.content
            try:
                text = json.loads(text, object_hook=datetime_decoder)
            except:
                pass

            return text

        return resposta.content

    def get_header(self, username, password):
        user_pass = b64encode(f"{username}:{password}".encode()).decode("ascii")
        headers = {
            'content-type': 'application/json',
            'Authorization': f'Basic {user_pass}',
            #'Authorization': 'Bearer ' + self.token
        }
        return headers

    def get_header_plain(self, username, password):
        user_pass = b64encode(f"{username}:{password}".encode()).decode("ascii")
        headers = {
            'Authorization': f'Basic {user_pass}',
        }
        return headers
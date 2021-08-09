import argparse
import os.path
import sys
import traceback

from camundacmd.api.deployment import Deployment


class DeployCommand:

    args: argparse.Namespace
    deployment: Deployment

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.deployment = Deployment()

    def _do_deploy(self, filename):
        changed_only = False

        if not filename or not os.path.isfile(filename):
            print(f'File {filename} not found!')
            sys.exit(1)

        # dir_list = os.listdir(".") if filename == '*' else [filename]
        dir_list = [filename]

        for file in dir_list:
            if file.endswith(".bpmn") or file.endswith(".cmmn"):
                deploy_ok = False
                try:
                    deploy = self.deployment.create(filename, changed_only, silent=True)

                    if deploy['deployedProcessDefinitions'] is None and deploy['deployedCaseDefinitions'] is None:
                        print(f'Deploy do arquivo {file} nao realizado.')
                        if filename != 'all':
                            sys.exit(0)
                    else:
                        deploy_ok = True

                except IOError:
                    traceback.print_exc()
                    print('Erro ao ler o arquivo!')
                    if filename != 'all':
                        sys.exit(1)
                except Exception as e:
                    traceback.print_exc()
                    print('Erro ao realizar o deploy no Camunda!')
                    if filename != 'all':
                        sys.exit(1)

                if deploy_ok:
                    print(f'Deploy de {file} realizado com sucesso!')
            else:
                print("Extensão inválida")

    def _do_list(self, key, only_latest_version):

        list = self.deployment.list(key, only_latest_version, silent=True)
        for l in list:
            print(f"{l['deploymentId']}\t{l['key']} version {l['version']} tag {l['versionTag']}")

    def _do_delete(self, id, cascade_delete=False):

        try:
            self.deployment.delete(id, cascade_delete, silent=True)
        except Exception as e:
            print(str(e))
            sys.exit(1)
        print("Definição removida!")

    def run(self):

        if 'file_name' in self.args:
            self._do_deploy(self.args.file_name)
        elif 'deployment_id' in self.args:
            cascade_delete = self.args.cascade_delete if 'cascade_delete' in self.args else False
            self._do_delete(self.args.deployment_id, cascade_delete)
        elif 'key_definition' in self.args:
            only_latest_version = self.args.only_latest_version if 'only_latest_version' in self.args else False
            self._do_list(self.args.key_definition, only_latest_version)
        else:
            print("Please select action: deploy, list or delete")


def main():
    #TODO: choose alt config figle
    #TODO: deploy all files in dir
    #TODO: delete all keys

    description = '''Deploy, undeploy or list definitions on a Camunda server'''
    parser = argparse.ArgumentParser(description=description, argument_default=argparse.SUPPRESS)
    subparsers = parser.add_subparsers(help='Commands')

    # List
    list_parser = subparsers.add_parser('list', help='List contents')
    list_parser.add_argument('-k', help='process key definition',  nargs='?', dest='key_definition')
    list_parser.add_argument('-o', help='show only latest versions', action='store_true', dest='only_latest_version')

    # Deploy
    deploy_parser = subparsers.add_parser('create', help='Create a deploy')
    deploy_parser.add_argument('file_name', help='file name')

    # Delete
    delete_parser = subparsers.add_parser('delete', help='Delete definitions')
    delete_parser.add_argument('deployment_id', help='deployment id')
    delete_parser.add_argument('-c', help='cascade delete', action='store_true', dest='cascade_delete')

    deployment = DeployCommand(parser.parse_args())
    deployment.run()


if __name__ == "__main__":
    main()
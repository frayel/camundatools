import argparse
import os.path
import sys
import traceback

from camundatools.definition import Definition
from camundatools.instance import Instance


class DefinitionCommand:

    args: argparse.Namespace
    definition: Definition
    instance: Instance

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.definition = Definition(silent=True, config_file=args.config_file)
        self.instance = Instance(silent=True, config_file=args.config_file)

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
                    deploy = self.definition.deploy(filename, changed_only)

                    if deploy['deployedProcessDefinitions'] is None and deploy['deployedCaseDefinitions'] is None:
                        print(f'Deployment of {file} failed.')
                        if filename != 'all':
                            sys.exit(0)
                    else:
                        deploy_ok = True

                except IOError:
                    traceback.print_exc()
                    print('File read error')
                    if filename != 'all':
                        sys.exit(1)
                except Exception as e:
                    traceback.print_exc()
                    print(f'Error trying to deploy {file}')
                    sys.exit(1)

                if deploy_ok:
                    print(f'Deployment of {file} sucessful!')
            else:
                print("Invalid extension!")

    def _do_list(self, key, only_latest_version):

        try:
            print(f"{'DeploymentId':<40} {'ProcessDefinitionKey':<30} {'Version':<8} {'Tag':<10}")
            print(f"{'-'*40:<40} {'-'*30:<30} {'-'*8:<8} {'-'*10:<10}")
            definitions = self.definition.list(key, only_latest_version)
            for d in definitions:
                print(f"{d['deploymentId']:<40} {d['key']:<30} {d['version']:<8} {d['versionTag'] or '':<10}")
        except Exception as e:
            print(str(e))
            sys.exit(1)

    def _do_delete(self, deployment_id, key_definition, cascade_delete):

        try:
            if key_definition:
                for definition in self.definition.list(key_definition):
                    self.definition.delete(definition['deploymentId'], cascade_delete)
            elif deployment_id:
                self.definition.delete(deployment_id, cascade_delete)
            else:
                raise Exception('Please inform a deployment id or a definition key')

        except Exception as e:
            print(str(e))
            sys.exit(1)
        print("Definition Deleted!")

    def _do_clear(self, key_definition):

        try:
            instances = self.instance.list(key_definition)
            for i in instances:
                print(f"Instance {i['id']} deleted.")
                self.instance.delete(i['id'], reason='Deleted from command line tool')

        except Exception as e:
            print(str(e))
            sys.exit(1)
        print(f"Definition {key_definition} cleared!")

    def _do_download(self, key_definition, file_name):
        try:
            xml = self.definition.get_xml(key_definition)
            filename = f"{xml['id']}.bpmn".replace(":", "_") if not file_name else file_name
            with open(filename, 'w') as file:
                file.write(xml['bpmn20Xml'])
            file.close()
            print(f'{filename} saved.')

        except Exception as e:
            print(str(e))
            sys.exit(1)

    def run(self, parser):

        if self.args.command == 'deploy':
            self._do_deploy(self.args.file_name)
        elif self.args.command == 'delete':
            deployment_id = self.args.deployment_id if 'deployment_id' in self.args else False
            key_definition = self.args.key_definition if 'key_definition' in self.args else False
            cascade_delete = self.args.cascade_delete if 'cascade_delete' in self.args else False
            self._do_delete(deployment_id, key_definition, cascade_delete)
        elif self.args.command == 'list':
            only_latest_version = self.args.only_latest_version if 'only_latest_version' in self.args else False
            self._do_list(self.args.key_definition, only_latest_version)
        elif self.args.command == 'clear':
            self._do_clear(self.args.key_definition)
        elif self.args.command == 'download':
            file_name = self.args.file_name if 'file_name' in self.args else False
            self._do_download(self.args.key_definition, file_name)
        else:
            parser.print_help()


def main():
    #TODO: deploy all files in dir

    description = '''Deploy, undeploy or list definitions on a Camunda server'''
    parser = argparse.ArgumentParser(description=description, argument_default=argparse.SUPPRESS)
    subparsers = parser.add_subparsers(help='Commands', dest="command")
    parser.add_argument('--cfg', help='config file', nargs='?', default='camundatools.cfg', dest='config_file')

    # List
    list_parser = subparsers.add_parser('list', help='List contents')
    list_parser.add_argument('-k', help='process key definition',  nargs='?', dest='key_definition')
    list_parser.add_argument('-o', help='show only latest versions', action='store_true', dest='only_latest_version')

    # Deploy
    deploy_parser = subparsers.add_parser('deploy', help='Deploy a definition')
    deploy_parser.add_argument('file_name', help='file name')

    # Delete
    delete_parser = subparsers.add_parser('delete', help='Delete a deployment')
    delete_parser.add_argument('-d', help='deployment id',  nargs='?', dest='deployment_id')
    delete_parser.add_argument('-k', help='process key definition',  nargs='?', dest='key_definition')
    delete_parser.add_argument('-c', help='cascade delete', action='store_true', dest='cascade_delete')

    # Clear
    clear_parser = subparsers.add_parser('clear', help='Clear all instances from a definition')
    clear_parser.add_argument('key_definition', help='process key definition')

    # Download
    download_parser = subparsers.add_parser('download', help='Download latest version of a XML definition from server')
    download_parser.add_argument('key_definition', help='process key definition')
    download_parser.add_argument('-f', help='output name', nargs='?', dest='file_name')

    deployment = DefinitionCommand(parser.parse_args())
    deployment.run(parser)


if __name__ == "__main__":
    main()


import argparse
import json
import sys

from camundatools.definition import Definition
from camundatools.instance import Instance


class InstanceCommand:

    args: argparse.Namespace
    instance: Instance
    definition: Definition

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.instance = Instance(silent=True, config_file=args.config_file)
        self.definition = Definition(silent=True, config_file=args.config_file)

    def _do_start(self, process_key, business_key, variables):
        try:
            result = self.instance.start_process(process_key, business_key, variables)
            print(f'Process instance started with id {result["id"]} and definition {result["definitionId"]}')
        except Exception as e:
            print(str(e))
            sys.exit(1)

    def _do_list(self, key_definition):
        try:
            print(f"{'ProcessInstanceId':<40} {'ProcessDefinitionKey':<30} {'Version':<8} {'BusinessKey':<12}")
            print(f"{'-'*40:<40} {'-'*30:<30} {'-'*8:<8} {'-'*10:<12}")
            instances = self.instance.list(key_definition)
            for i in instances:
                d = self.definition.inspect(i['definitionId'])
                print(f"{i['id']:<40} {d['key']:<30} {d['version']:<8} {i['businessKey'] or i['caseInstanceId'] or '':<12}")
        except Exception as e:
            print(str(e))
            sys.exit(1)

    def _do_inspect(self, process_instance_id):
        try:
            result = self.instance.inspect(process_instance_id)
            print(json.dumps(result, indent=4, sort_keys=True, default=str))
        except Exception as e:
            print(str(e))
            sys.exit(1)

    def _do_find(self, process_key, business_key):
        try:
            result = self.instance.find(process_key, business_key)
            print(json.dumps(result, indent=4, sort_keys=True, default=str))
        except Exception as e:
            print(str(e))
            sys.exit(1)

    def _do_delete(self, process_instance_id, reason):
        try:
            result = self.instance.delete(process_instance_id, reason)
            print(f'Instance deleted!')
        except Exception as e:
            print(str(e))
            sys.exit(1)

    def _do_download(self, process_instance_id, file_name):
        try:
            result = self.instance.inspect(process_instance_id)
            xml = self.instance.get_xml(result["definitionId"])
            filename = f"{xml['id']}.bpmn".replace(":", "_") if not file_name else file_name
            with open(filename, 'w') as file:
                file.write(xml['bpmn20Xml'])
            file.close()
            print(f'{filename} saved.')

        except Exception as e:
            print(str(e))
            sys.exit(1)

    def _do_migrate(self, key_definition, business_key, source_activity, target_activity):
        try:
            for instance in self.instance.list(key_definition, business_key):
                instance = self.instance.inspect(instance['id'])
                definition = self.instance.inspect(instance['definitionId'])
                last_definition = self.instance.inspect(definition['key'])
                if last_definition['id'] != instance['definitionId']:
                    instructions = list()
                    for atividade in self.task.list(instance['id']):
                        instruction = dict()
                        instruction["sourceActivityIds"] = [source_activity] if source_activity else [atividade["taskDefinitionKey"]]
                        instruction["targetActivityIds"] = [target_activity] if target_activity else [atividade["taskDefinitionKey"]]
                        instructions.append(instruction)
                        # if instructions and len(instructions) > 0:
                        print(f"Migrating {definition['key']} {instance['id']}: {definition['versionTag']} ({definition['version']}) -> {last_definition['versionTag']} ({last_definition['version']})")
                        result = self.instance.migrate([instance['id']], instance['definitionId'], last_definition['id'], instructions)
                        for k in instructions:
                            print(f'Task migrated from {k["sourceActivityIds"]} to {k["targetActivityIds"]}')
                        # else:
                        #     print(f"There are no tasks to migrate in {definition['key']} {intance['id']}")

            print('Finished migrations.')
        except Exception as e:
            print(str(e))
            sys.exit(1)

    def run(self, parser):

        if self.args.command == 'start':
            variables = self.args.variables if 'variables' in self.args else None
            self._do_start(self.args.key_definition, self.args.business_key, variables)
        elif self.args.command == 'list':
            key_definition = self.args.key_definition if 'key_definition' in self.args else None
            self._do_list(key_definition)
        elif self.args.command == 'inspect':
            self._do_inspect(self.args.id)
        elif self.args.command == 'find':
            self._do_find(self.args.key_definition, self.args.business_key)
        elif self.args.command == 'delete':
            self._do_delete(self.args.id, self.args.reason)
        elif self.args.command == 'download':
            file_name = self.args.file_name if 'file_name' in self.args else False
            self._do_download(self.args.id, file_name)
        elif self.args.command == 'migrate':
            key_definition = self.args.key_definition if 'key_definition' in self.args else None
            business_key = self.args.business_key if 'business_key' in self.args else None
            source_activity = self.args.source_activity if 'source_activity' in self.args else None
            target_activity = self.args.target_activity if 'target_activity' in self.args else None
            self._do_migrate(key_definition, business_key, source_activity, target_activity)
        else:
            parser.print_help()


def main():
    #TODO: start with a json var file

    description = '''Manage process instances on a Camunda server'''
    parser = argparse.ArgumentParser(description=description, argument_default=argparse.SUPPRESS)
    subparsers = parser.add_subparsers(help='Commands', dest='command')
    parser.add_argument('--cfg', help='config file', nargs='?', default='camundatools.cfg', dest='config_file')

    # Start
    start_parser = subparsers.add_parser('start', help='Start a process instance')
    start_parser.add_argument('key_definition', help='process key definition')
    start_parser.add_argument('business_key', help='business key')
    start_parser.add_argument('-v', help='process variables',  nargs='?', dest='variables')

    # List
    list_parser = subparsers.add_parser('list', help='List process instances')
    list_parser.add_argument('-k', help='process key definition', nargs='?', dest='key_definition')

    # Inspect
    inspect_parser = subparsers.add_parser('inspect', help='Inspect a process instance')
    inspect_parser.add_argument('id', help='process instance id')

    # Find
    find_parser = subparsers.add_parser('find', help='Find a process instance by business key')
    find_parser.add_argument('key_definition', help='process key definition')
    find_parser.add_argument('business_key', help='business key')

    # Delete
    cancel_parser = subparsers.add_parser('delete', help='Delete a process instance')
    cancel_parser.add_argument('id', help='process instance id')
    cancel_parser.add_argument('reason', help='delete reason')

    # Migrate
    migrate_parser = subparsers.add_parser('migrate', help='Migrate a process instance to a newer definition')
    migrate_parser.add_argument('-k', help='process key definition', nargs='?', dest='key_definition')
    migrate_parser.add_argument('-b', help='business key', nargs='?', dest='business_key')
    migrate_parser.add_argument('-s', '--source', help='source activity', nargs='?', dest='source_activity')
    migrate_parser.add_argument('-t', '--target', help='target activity', nargs='?', dest='target_activity')

    # Download
    download_parser = subparsers.add_parser('download', help='Download a XML of the process instance')
    download_parser.add_argument('id', help='process instance id')
    download_parser.add_argument('-f', help='output name', nargs='?', dest='file_name')

    deployment = InstanceCommand(parser.parse_args())
    deployment.run(parser)


if __name__ == "__main__":
    main()
import argparse
import json
import sys

from camundatools.instance import Instance
from camundatools.task import Task


class TaskCommand:

    args: argparse.Namespace
    task: Task
    instance: Instance

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.task = Task(silent=True, config_file=args.config_file)
        self.instance = Instance(silent=True, config_file=args.config_file)

    def _do_list(self, key_definition, business_key, candidate_group, task_name, variable_value, page):
        try:
            query_vars = None
            if variable_value:
                if '=' in variable_value:
                    v = variable_value.split('=')
                    if len(v) == 2:
                        query_vars = [{
                            'name': v[0],
                            'value': v[1],
                            'operator': 'eq',
                        }]
                    else:
                        raise Exception('variable_value must be a "variable=value"')
                else:
                    raise Exception('variable_value must be a "variable=value"')

            print(f"{'TaskId':<40} {'TaskDefinitionKey':<30} {'TaskName':<40}")
            print(f"{'-'*40:<40} {'-'*30:<30} {'-'*40:<40}")
            tasks = self.task.list(process_key=key_definition, business_key=business_key,
                                   candidate_groups=candidate_group, task_name=task_name, query_vars=query_vars,
                                   page=page)
            for t in tasks:
                t['name'] = t['name'].replace('\n', ' ')
                print(f"{t['id']:<40} {t['taskDefinitionKey']:<30} {t['name']:<40}")
        except Exception as e:
            print(str(e))
            sys.exit(1)

    def _do_inspect(self, task_id):
        try:
            result = self.task.inspect(task_id)
            print(json.dumps(result, indent=4, sort_keys=True, default=str))
        except Exception as e:
            print(str(e))
            sys.exit(1)

    def _do_complete(self, process_key, business_key):
        try:
            result = self.instance.find(process_key, business_key)
            print(result)
        except Exception as e:
            print(str(e))
            sys.exit(1)

    def _do_delete(self, task_id):
        try:
            result = self.task.delete(task_id)
            print(f'Instance deleted!')
        except Exception as e:
            print(str(e))
            sys.exit(1)

    def _do_move(self, task_id, target_task_name):
        try:
            task = self.task.inspect(task_id)
            instructions = {
                "instructions": [
                    {
                        "type": "startBeforeActivity",
                        "activityId": target_task_name,
                    },
                    {
                        "type": "cancel",
                        "activityId": task['taskDefinitionKey'],
                    }
                ]
            }
            self.instance.modify(task['processInstanceId'], instructions)
            print('Task Moved!')

        except Exception as e:
            print(str(e))
            sys.exit(1)

    def run(self, parser):

        if self.args.command == 'list':
            key_definition = self.args.key_definition if 'key_definition' in self.args else None
            business_key = self.args.business_key if 'business_key' in self.args else None
            candidate_group = self.args.candidate_group if 'candidate_group' in self.args else None
            task_name = self.args.task_name if 'task_name' in self.args else None
            variable_value = self.args.variable_value if 'variable_value' in self.args else None
            page = self.args.page if 'page' in self.args else None
            self._do_list(key_definition, business_key, candidate_group, task_name, variable_value, page)
        elif self.args.command == 'inspect':
            self._do_inspect(self.args.id)
        elif self.args.command == 'complete':
            variables = self.args.variables if 'variables' in self.args else None
            self._do_complete(self.args.id, variables)
        elif self.args.command == 'delete':
            self._do_delete(self.args.id)
        elif self.args.command == 'move':
            self._do_move(self.args.id, self.args.target)
        else:
            parser.print_help()


def main():
    #TODO: complete with a json vars file
    #TODO: inspect by process and business key

    description = '''Manage tasks on a Camunda server'''
    parser = argparse.ArgumentParser(description=description, argument_default=argparse.SUPPRESS)
    subparsers = parser.add_subparsers(help='Commands', dest='command')
    parser.add_argument('--cfg', help='config file', nargs='?', default='camundatools.cfg', dest='config_file')

    # List
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('-k', help='process key definition', nargs='?', dest='key_definition')
    list_parser.add_argument('-b', help='business key', nargs='?', dest='business_key')
    list_parser.add_argument('-c', help='candidate group', nargs='?', dest='candidate_group')
    list_parser.add_argument('-t', help='task name', nargs='?', dest='task_name')
    list_parser.add_argument('-v', help='variable=value', nargs='?', dest='variable_value')
    list_parser.add_argument('-p', help='page', nargs='?', dest='page')

    # Inspect
    inspect_parser = subparsers.add_parser('inspect', help='Inspect a task')
    inspect_parser.add_argument('id', help='task id')

    # Complete
    complete_parser = subparsers.add_parser('complete', help='complete a task')
    complete_parser.add_argument('id', help='task id')
    complete_parser.add_argument('-v', help='process variables',  nargs='?', dest='variables')

    # Delete
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('id', help='task id')

    # Move
    move_parser = subparsers.add_parser('move', help='Move a task to other activity')
    move_parser.add_argument('id', help='process instance id')
    move_parser.add_argument('target', help='target activity')

    deployment = TaskCommand(parser.parse_args())
    deployment.run(parser)


if __name__ == "__main__":
    main()
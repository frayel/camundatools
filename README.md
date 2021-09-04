# CamundaTools

CamundaTools is a Python REST api client for the workflow and decision automation engine Camunda.
It will provide a simple and intuitive interface for the most used features of the rest-engine api.

CamundaTools also has a set of command line tools to manage definitions, instances and tasks.

## Author
Felipe Rayel <felipe.rayel@gmail.com>

## Install
pip install camundatools

## Setup
Create a file in the root path  called camundatools.cfg
```editorconfig
[config]
CAMUNDA_API_BASE_URL = http://localhost:8080/engine-rest
CAMUNDA_AUTH_USERNAME = demo
CAMUNDA_AUTH_PASSWORD = demo
REQUEST_RETRY = 3
REQUEST_TIMEOUT = 5
EXTERNAL_MAX_TASKS = 10
EXTERNAL_TASK_LOCK_DURATION_IN_MILISECONDS = 30000
EXTERNAL_TASK_RETRY_TIMEOUT = 300000
MAX_RESULTS_PER_PAGE = 100
MAX_RESULTS_NON_PAGINATED = 100
# CERT_FILE = cert_file.pem
```

## Command Line Tools

### Definition Command Parameters
    list                List deployed process definitions
    deploy              Deploy a definition
    delete              Delete a deployment
    clear               Clear all instances from a definition
    download            Download latest version of a XML definition from server

### Example:
```bash
$> definition list
$> definition deploy <filename.bpmn>
$> definition delete <deployment_id>
$> definition clear <definition_key>
$> definition download <definition_key>
```
### Instance Command Parameters
    start               Start a process instance
    list                List process instances
    inspect             Inspect a process instance
    find                Find a process instance by business key
    delete              Delete a process instance
    migrate             Migrate a process instance to a newer definition
    download            Download a XML of the process instance

### Example:
```bash
$> instance start <process_key> <business_key>
$> instance list
$> instance inspect <process_instance_id>
$> instance find <process_key> <business_key>
$> instance delete <process_instance_id> <reason>
$> instance migrate
```
### Task Command Parameters
    list                List tasks
    inspect             Inspect a task
    complete            complete a task
    delete              Delete a task
    move                Move a task to other activity

### Example:
```bash
$> task list
$> task inspect <task_id>
$> task complete <task_id>
$> task delete <task_id>
$> task move <process_instance_id> <new_task_name>
```

# Using the API

### Deploy a bpm
    definition_api = Definition('http://localhost:8080/engine-rest', 'demo', 'demo')
    definition_api.deploy('file.bpmn')

### List Instance
    instance_api = Instance('http://localhost:8080/engine-rest', 'demo', 'demo')
    instances = instance_api.list('myProcessKeyDefinition')
    for instance in instances:
        print(instance)
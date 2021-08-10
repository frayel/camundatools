# CamundaTools

CamundaTools is a Python REST api client for the workflow and decision automation engine Camunda.
It will provide a simple and intuitive interface for the most used features of the rest-engine api.

CamundaTools also has a set of command line tools to manage definitions, instances and tasks.

## Author
Felipe Rayel <felipe.rayel@gmail.com>

## Install
?

## Setup
Create a file in the root path  called camundatools.cfg
```editorconfig
[config]
CAMUNDA_API_BASE_URL = http://localhost:8080/engine-rest
CAMUNDA_AUTH_USERNAME = demo
CAMUNDA_AUTH_PASSWORD = demo
REQUEST_RETRY = 3
REQUEST_TIMEOUT = 10
ARQUIVO_CERTIFICADO =
MAX_RESULTS_PER_PAGE = 100
MAX_RESULTS_NON_PAGINATED = 100
```

## Command Line Tools

### Definition Command
    list                List contents
    deploy              Deploy a definition
    delete              Delete a definition

```bash
$> definition list
$> definition deploy filename.bpmn
$> definition delete deployment_id
```
### Instance Command
    start               Start a process instance
    list                List process instances
    inspect             Inspect a process instance
    find                Find a process instance by business key
    delete              Delete a process instance
    migrate             Migrate a process instance to a newer definition

```bash
$> instance start
$> instance list
$> instance inspect
$> instance find
$> instance delete
$> instance migrate
```
### Task Command
    list                List tasks
    inspect             Inspect a task
    complete            complete a task
    delete              Delete a task
    move                Move a task to other activity

```bash
$> task list
$> task inspect
$> task complete
$> task delete
$> task move
```

# API

### Deploy a bpm
    definition_api = Definition('http://localhost:8080/engine-rest', 'demo', 'demo')
    definition_api.deploy('file.bpmn')

### List Instance
    instance_api = Instance('http://localhost:8080/engine-rest', 'demo', 'demo')
    instances = instance_api.list('myProcessKeyDefinition')
    for instance in instances:
        print(instance)

# CamundaTools

CamundaTools is a Python REST api client for the workflow and decision automation engine Camunda.

CamundaTools takes care of Camunda-specific characteristics and gives you an intuitive Python 
interface so you can focus on developing your actual business application. 
So CamundaTools deals with http requests, nested dictionaries, camelCase keys, 
datetime formatting and more for you.
CamundaTools also bring command-line utils to manage deployment, instances and tasks.

# Deploy a bpm
    deployment = Deployment('http://localhost:8080/engine-rest', 'demo', 'demo')
    deploy = deployment.deploy_bpmn('file.bpmn')

# Tools:
```bash
$> deploy list
$> deploy create file
```
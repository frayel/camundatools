
# CamundaCmd

CamundaCmd is a Python REST api client for the workflow and decision automation engine Camunda.

CamundaCmd takes care of Camunda-specific characteristics and gives you an intuitive Python 
interface so you can focus on developing your actual business application. 
So CamundaCmd deals with http requests, nested dictionaries, camelCase keys, 
datetime formatting and more for you.
CamundaCmd also bring command-line utils to manage deployment, instances and tasks.

# Deploy a bpm
    deployment = Deployment('http://localhost:8080/engine-rest', 'demo', 'demo')
    deploy = deployment.deploy_bpmn('file.bpmn')
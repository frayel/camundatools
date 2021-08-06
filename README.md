
# Teste Django + Celery + RabbitMQ

# RabbitMQ
Primeiro é necessario um broker de messageria. Rodar o RabbitMQ:  

```sh
$> docker run --net rede_teste --ip 172.18.0.2 -d --hostname rabbitmq --name rabbitmq -p 5672:5672 rabbitmq
```
# Celery Worker
Para consumir a fila é necessário um worker.  
OBS: Para rodar em windows é necessário o parâmetro "-P gevent"
```sh
$> celery -A app worker -l info -P gevent
```

# Celery Beat
O Beat executará tarefas agendadas, mas nao é necessário para o worker funcionar
```sh
$> celery -A app beat -l info
```

# Executar o teste
Executando o comando abaixo, será chamada a função tasks.wait_seconds passando como parâmetro o número
de segundos que ela deve aguardar.  

O backend usado é o django-db, portanto o resultado do processamento da fila será gravado na tabela: django_celery_results_taskresult
```sh
$> python manage.py teste 10
```
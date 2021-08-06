
# Teste Django + Kafka

# Kafka
Primeiro é necessario subir os dockers  

```sh
$> docker-compose up -d
```
# Criar um Topico
```sh
$> docker exec broker kafka-topics --bootstrap-server broker:9092 --create --topic topico_teste
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
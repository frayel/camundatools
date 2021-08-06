
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

# Executar o teste

Executar o producer para colocar uma mensagem na fila:
```sh
$> python manage.py send Mensagem
```

Executar o consumer, para processar as mensagens pendentes na fila:
```sh
$> python manage.py receive
```
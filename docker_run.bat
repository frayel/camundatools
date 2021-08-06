@echo off
docker stop rabbitmq
docker rm rabbitmq
docker rmi rabbitmq
docker volume prune
docker network create --subnet=172.18.0.0/16 rede_teste
docker run --net rede_teste --ip 172.18.0.2 -d --hostname rabbitmq --name rabbitmq -p 5672:5672 rabbitmq


Para rodar em windows é necessario o parametro "-P gevent"
celery -A app worker -l info -P gevent
celery -A app beat -l info


python manage.py teste 10
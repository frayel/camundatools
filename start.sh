#!/usr/bin/env bash

export DJANGO_SETTINGS_MODULE="consultation.settings-prd"
cd consultation
python manage.py migrate
python manage.py loaddata initial_data
# Executa o scheduler em background
setsid nohup python3 manage.py start_scheduler > /opt/app/scheduler.log 2>&1 &
# Executa a aplicação
gunicorn consultation.wsgi --user www-data --bind 0.0.0.0:8010 --workers 3

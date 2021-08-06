FROM python:3.9

RUN mkdir -p /opt/app
RUN mkdir -p /opt/app/consultation
COPY requirements.txt start.sh /opt/app/
COPY consultation /opt/app/consultation/
WORKDIR /opt/app
RUN pip install -r requirements.txt
RUN pip install gunicorn
RUN chown -R www-data:www-data /opt/app

EXPOSE 8010
ENTRYPOINT ["sh", "/opt/app/start.sh"]
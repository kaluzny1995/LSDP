FROM python:3.7 
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1

COPY requirements.txt ./  
RUN pip install --no-cache-dir -r requirements.txt  && rm requirements.txt

RUN useradd -ms /bin/bash celery

ENV CELERY_BROKER_URL="amqp://guest:guest@rabbitmq:5672"
ENV CELERY_RESULT_BACKEND="rpc"

WORKDIR /app
COPY app ./

RUN chown -R celery:celery /app
RUN chmod 755 /app

USER celery

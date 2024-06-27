FROM python:3.12-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'config.settings'

RUN apt-get update &&\
    apt-get -y install build-essential &&\
    apt-get clean &&\
    rm -rf /var/lib/apt/lists/* &&\
    apt-get autoremove -y &&\
    apt-get autoclean

RUN mkdir -p /var/www/static/ &&\
    mkdir -p /var/www/media/ &&\
    mkdir -p /opt/app/static/ &&\
    mkdir -p /opt/app/media/ &&\
    groupadd -r app && useradd -r -g app app && chown app:app -R /app

COPY requirements.txt requirements.txt
RUN python3.12 -m pip install --no-cache-dir --upgrade pip &&\
    python3.12 -m pip install --no-cache-dir -r requirements.txt

USER app:app

COPY . .
COPY uwsgi/uwsgi.ini uwsgi.ini

EXPOSE 8000/tcp

ENTRYPOINT ["uwsgi", "--strict", "--ini", "uwsgi.ini"]
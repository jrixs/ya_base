FROM python:3.12-slim
VOLUME /etl:rw
WORKDIR /etl


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update &&\
    apt-get -y install curl &&\
    apt-get clean &&\
    rm -rf /var/lib/apt/lists/* &&\
    apt-get autoremove -y &&\
    apt-get autoclean

RUN groupadd -r app && useradd -r -g app app && chown app:app -R /etl && chmod 777 -R /etl

COPY requirements.txt requirements.txt
RUN python3.12 -m pip install --no-cache-dir --upgrade pip &&\
    python3.12 -m pip install --no-cache-dir -r requirements.txt

USER app:app

COPY ./postgres_to_es .

CMD /bin/sh set_index.sh && python3.12 etl_start.py
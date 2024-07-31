FROM python:3.12-slim
WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN groupadd -r auth && useradd -r -g auth auth && chown auth:auth -R /src

COPY ./requirements.txt requirements.txt
RUN python3.12 -m pip install --no-cache-dir --upgrade pip &&\
    python3.12 -m pip install --no-cache-dir -r requirements.txt

USER auth:auth

COPY ./src .

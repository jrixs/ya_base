FROM python:3.8-slim
WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN groupadd -r backend && useradd -r -g backend backend && chown backend:backend -R /src

COPY src/requirements.txt requirements.txt
RUN python3.8 -m pip install --no-cache-dir --upgrade pip &&\
    python3.8 -m pip install --no-cache-dir -r requirements.txt

USER backend:backend

COPY ./src .

ENTRYPOINT ["python", "run_backend.py"]
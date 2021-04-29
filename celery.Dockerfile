FROM python:3.8.3-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y curl build-essential
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
RUN ~/.poetry/bin/poetry export -o /tmp/requirements.txt
RUN pip install -U pip wheel setuptools
RUN pip install -r /tmp/requirements.txt

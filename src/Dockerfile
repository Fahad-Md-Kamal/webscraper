# FROM python:3.10-alpine3.16
FROM python:3.9.5-slim
LABEL key="faahad.hossain@gmail.com"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
COPY ./ ./

WORKDIR /.

RUN pip install -r /requirements.txt

FROM python:3.9.5-slim
LABEL key="faahad.hossain@gmail.com"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
COPY ./src /src

WORKDIR /src

RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

# pull official base image
FROM python:3.9.5-slim-buster

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ADD . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

WORKDIR /app/code
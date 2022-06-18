# pull official base image
FROM python:3.9.5-slim-buster

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ADD . /alice
WORKDIR /alice

RUN pip3 install -r requirements.txt

WORKDIR /alice/code
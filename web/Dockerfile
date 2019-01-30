FROM python:3.6-alpine
MAINTAINER devops@raccoongang.com
ENV PYTHONUNBUFFERED 1
RUN apk --update add postgresql-dev alpine-sdk
RUN mkdir /olga
WORKDIR /olga
ADD requirements.txt /olga/requirements.txt
RUN pip install -r requirements.txt

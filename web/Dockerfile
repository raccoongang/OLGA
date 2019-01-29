FROM python:3.7-alpine
MAINTAINER devops@raccoongang.com
ENV PYTHONUNBUFFERED 1
RUN apk --update add postgresql-dev alpine-sdk
RUN pip install --upgrade pip
RUN mkdir /olga
WORKDIR /olga
ADD requirements.txt /olga/requirements.txt
RUN pip3 install -r requirements.txt

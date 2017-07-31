FROM python:2.7-alpine
MAINTAINER devops@raccoongang.com
ENV PYTHONUNBUFFERED 1
RUN mkdir /acceptor
WORKDIR /acceptor
ADD requirements.txt /acceptor/requirements.txt
RUN apk --update add postgresql-dev alpine-sdk
RUN pip install -r requirements.txt 
ADD . /acceptor

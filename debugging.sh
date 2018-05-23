#!/bin/bash
docker-compose -f local-compose.yml stop olga
docker-compose -f local-compose.yml run --service-ports olga python manage.py runserver 0.0.0.0:7000
docker-compose -f local-compose.yml start olga

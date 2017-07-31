# acceptor

Acceptor server which takes specific data from edx-platform and visualizes the data on the world map.

# installations

Install Docker CE: https://www.docker.com/community-edition
Most of installation packages include docker-compose, but if it was not installed on your system, do it: https://docs.docker.com/compose/install/

# local development

Build containers:

``` 
   $ docker-compose -f local-compose.yml build
```

Make migrations:

```
   $ docker-compose -f local-compose.yml run acceptor python manage.py migrate
```

Create superuser:

```
   $ docker-compose -f local-compose.yml run acceptor python manage.py createsuperuser
```

Run Django (runserver) and PostgreSQL containers. Django will be available on http://localhost:8000/
```
   $ docker-compose -f local-compose.yml up
```

# Run on server

Install Docker CE: https://www.docker.com/community-edition
Most of installation packages include docker-compose, but if it was not installed on your system, do it: https://docs.docker.com/compose/install/

Build containers:

``` 
   $ docker-compose -f docker-compose.yml build
```

Make migrations:

```
   $ docker-compose -f docker-compose.yml run acceptor python manage.py migrate
```

Create superuser:

```
   $ docker-compose -f docker-compose.yml run acceptor python manage.py createsuperuser
```

Run Django and PostgreSQL containers. Django will be available on http://server-ip-or-domain/

```
   #### TODO: Rewtire PostgreSQL configuration and mount to host folder.
   $ docker-compose -f docker-compose.yml up -d

```
some changes

# acceptor
Acceptor server which takes specific data from edx-platform and visualizes the data on the world map.

# installations
Install requirements:
```
   $ pip install -r requirements.txt
```
Make migrations:
```
   $ python manage.py migrate
```
Run the server:
```
   $ python manage.py runserver
```

# local development
Install requirements:
``` 
   $ pip install -r requirements.txt
```
Rename:
```
   local_settings.py.example to private.py
```

Make migrations:
```
   $ python manage.py migrate
```
Create superuser:
```
   $ python manage.py createsuperuser
```
Load fixtures:
```
   $ cd graph_creator
   $ python utils.py
   $ python ../manage.py loaddata test_fixture.json
```
Run the server:
```
   $ python manage.py runserver
```

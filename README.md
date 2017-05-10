# acceptor
Acceptor server which takes specific data from edx-platform and visualizes the data on the world map.

# installations

pip install -r requirements.txt
python manage.py migrate

# local development

python manage.py runserver
rename local_settings.py.example to private.py
python manage.py createsuperuser
python manage.py loaddata graph_creator

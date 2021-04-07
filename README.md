# OLGA [ARCHIVED]

[![Travis](https://travis-ci.org/raccoongang/OLGA.svg?branch=develop)](https://travis-ci.org/raccoongang/OLGA)
[![Codecov](https://codecov.io/gh/raccoongang/OLGA/branch/develop/graph/badge.svg)](https://codecov.io/gh/raccoongang/OLGA/branch/develop)
[![Release](https://img.shields.io/github/release/raccoongang/OLGA.svg)](https://github.com/raccoongang/OLGA/releases)
[![Code Climate](https://img.shields.io/codeclimate/github/raccoongang/OLGA.svg)](https://codeclimate.com/github/raccoongang/OLGA)

OLGA has arisen out of [Open edX ](https://open.edx.org) requirement to collect edX platform installations
statistics data from all over the world. OLGA is  required to be able to collect, visualize and process this data
according to legal rules. In general, it provides possibilities for analysing trends of platform usage and users
engagement in e-learning process per country and globally around the world.

## Installation

[Install Docker CE](https://www.docker.com/community-edition). 
Most of installation packages include docker-compose, but if it was not installed on your system, [do it](https://docs.docker.com/compose/install). 

## Development

Clone OLGA repository to your local machine under virtual environment:

```
    $ git clone https://github.com/raccoongang/OLGA.git
```

Build container:

```
    $ docker-compose -f local-compose.yml build
```

Make migrations:

```
    $ docker-compose -f local-compose.yml run olga python manage.py migrate
```

Create superuser:

```
    $ docker-compose -f local-compose.yml run olga python manage.py createsuperuser
```

Run Django (runserver) and PostgreSQL containers. Django will be available on port `7000`.

```
    $ docker-compose -f local-compose.yml up
```

Environment will get bunch of linters, that you are able to use via:

```
    $ cd web && pep8 && flake8 & pylint olga && cd ..
```

### Tests

To run tests use command below:

```
    $ docker-compose -f local-compose.yml run olga python manage.py test
```

## Production

[things]

## API

OLGA receives statistics through own API, that provides next endpoints:

`/api/token/registration/`
* GET: register edX platform.
    * Parameters: access_token.
    * Return `201` if token was successfully created.

`/api/token/authorization/`
* GET: authorize edX platform.
    * Parameters: access_token.
    * Return `200` if token was successfully authorized.
    * Return `401` if token was unsuccessfully authorized.
    
`/api/installation/statistics/`
* GET: receive edX platform's statistics.
    * Parameters for `paranoid` level: 
        * `access_token`
        * `active_students_amount_day`
        * `active_students_amount_week`
        * `active_students_amount_month`
        * `courses_amount`
        * `statistics_level`
    * Parameters for `enthusiast` level (extends `paranoid` data ): 
        * `latitude` (not used for now)
        * `longitude` (not used for now)
        * `platform_name`
        * `platform_url`
        * `students_per_country`
    * Return `201` if statistics was successfully delivered.
    * Return `401` if token was unsuccessfully authorized.

## Statistics visualization details

OLGA provides three graphs for instances, courses and active students, which have been gathered from the start of collecting till now.

![olga_students_graph](https://user-images.githubusercontent.com/22666467/27955348-17c4d3dc-631d-11e7-812a-43a5bdffbf90.png)

In addition, OLGA comprises `Global Activity Metrics` which show instances, courses and active students amounts for the last calendar day.

![olga_activity_metrics_graphs](https://user-images.githubusercontent.com/22666467/27955707-b20a647e-631e-11e7-86ef-77a1da22f71c.png)

Besides that you are able to interact with world map, that contains darker marker for students amount, also for last calendar day.

![olga_world_map](https://user-images.githubusercontent.com/22666467/27955282-c92b20aa-631c-11e7-96da-0fec7b25a12a.png)

As well as graphs interface, OLGA has `Global Activity Metrics` for top country by students amount and countries in statistics amount.

![olga_activity_metrics_map](https://user-images.githubusercontent.com/22666467/27955718-c9737042-631e-11e7-8fee-c8dd1803edd8.png)

Full report based on world map's `Global Activity Metrics` located within `Geographic Breakdown` table.

![olga_geographic_breakdown](https://user-images.githubusercontent.com/22666467/27955328-f78b8bba-631c-11e7-9ef9-b7db7cdfa3cd.png)

## License

The code in this repository is licensed under the AGPL v3 licence unless another noted.

Please see [LICENSE](https://github.com/raccoongang/OLGA/blob/master/LICENSE) file for details.

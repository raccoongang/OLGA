# acceptor

[![Build Status](https://travis-ci.org/raccoongang/acceptor.svg?branch=master)](https://travis-ci.org/raccoongang/acceptor)
[coverage]
[release]

Acceptor arose out of [Open edX ](https://open.edx.org) requirement to collect statistics data from edx platform
installations all over the world. Acceptor is  required to be able to collect, visualize and process this data
according to legal rules. In general it provides possibilities for analysing trends of platform usage and users
engagement in e-learning process per country and globally around the world.

## Installation

Clone Acceptor repository to your local machine under virtual environment:

```
git clone https://github.com/raccoongang/xblock-video.git
```

Install all dependencies with:

```
pip install -r requirements.txt
```

Do migrate command and you are able to run server and start develop:

```
./manage.py migrate
```

## Development

Also you can follow code quality way and install development requirements:

```
pip install -r requirements_dev.txt
```

Environment will get bunch of linters, that you are able to use via:

```
flake8 && pep8 && pylint olga
```

## Production

[things]

## Statistics visualization details

Acceptor provides three graphs for instances, courses and activity students, that it gathered from the start of collecting to now.

![olga_students_graph](https://user-images.githubusercontent.com/22666467/27955348-17c4d3dc-631d-11e7-812a-43a5bdffbf90.png)

Addition, Acceptor has `Global Activity Metrics`, that show instances, courses and active students amounts for last calendar day.

![olga_activity_metrics_graphs](https://user-images.githubusercontent.com/22666467/27955707-b20a647e-631e-11e7-86ef-77a1da22f71c.png)

Besides that, also for last calendar day, you are able to interact with world map, that contains darker marker for students amount.

![olga_world_map](https://user-images.githubusercontent.com/22666467/27955282-c92b20aa-631c-11e7-96da-0fec7b25a12a.png)

As well as graphs interface, Acceptor has `Global Activity Metrics` for top country by students amount and countries in statistics amount.

![olga_activity_metrics_map](https://user-images.githubusercontent.com/22666467/27955718-c9737042-631e-11e7-8fee-c8dd1803edd8.png)

Full report based on world map's `Global Activity Metrics` located within `Geographic Breakdown` table.

![olga_geographic_breakdown](https://user-images.githubusercontent.com/22666467/27955328-f78b8bba-631c-11e7-9ef9-b7db7cdfa3cd.png)

## License

The code in this repository is licensed under the AGPL v3 licence unless otherwise noted.

Please see [LICENSE](https://github.com/raccoongang/acceptor/blob/master/LICENSE) file for details.

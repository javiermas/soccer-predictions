# soccer-predictions
Project for predicting soccer results

## Installation

### Requirements

```
virtualenv --python=python3.8 env
source env/bin/activate
pip install -e .
```

## Set-up

Airflow requires a postgreSQL database to store information, we can start it with:
```
pg_ctl -D /usr/local/var/postgres start
```

```
redis-server --daemonize yes \
    && airflow initdb \
    && airflow scheduler -D \
    && airflow webserver -D \
    && airflow trigger_dag deployment -sd dags
```

## Repository structure
```
├── soccerlearn
│   ├── api
│   ├── data
│   ├── features
│   ├── jobs
│   └── utils
├── figs
├── notebooks
├── main.py
├── README.md
└── .gitignore
```

## References
https://github.com/brianlan/Whoscored/blob/master/crawl_player_match_level_data.py

https://doctorspin.me/digital-strategy/machine-learning/

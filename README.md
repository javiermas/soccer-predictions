![master-CI](https://github.com/javiermas/soccer-predictions/workflows/master-CI/badge.svg)

# soccer-predictions

Project for predicting soccer results

## Installation

### Requirements

We need a mysql db for Celery
```
brew install mysql
brew services start mysql
sudo mysql -e 'CREATE USER airflow@localhost'
sudo mysql -e 'CREATE DATABASE airflow'
sudo mysql -e "GRANT ALL PRIVILEGES ON airflow.* TO airflow"
```

```
virtualenv --python=python3.8 env
source env/bin/activate
pip install -e .
```

## Set-up

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

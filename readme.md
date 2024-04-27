# Job Scraper 

Scrap Jobs from various sources and save them to DB.
![Alt text](./HLD.svg)
<img src="./hld.svg">
----

Here are the steps for getting your system initially setup.

### Install python dependencies
This project assumes you already have [virtualenv, virtualenvwrapper](http://docs.python-guide.org/en/latest/dev/virtualenvs/) and [autoenv](https://github.com/kennethreitz/autoenv) installed globally on your system.

First, create a new virtual environment:

    $ mkvirtualenv jobscraper
    $ virtualenv activate

Then, install the required python dependencies

    $ pip install -r requirements.txt

### Setup local postgres database
Run a postgres instance locally ( depends on your operating system. For mac its ```brew services start postgres``` ). Once done do the following:
    
    //connect to the postgres using psql
    $ psql -h localhost -d postgres

    psql (10.1)
    Type "help" for help.

    //create DB called jobscraper
    postgres=# CREATE DATABASE jobscraper;
    CREATE DATABASE

    //create user postgres
    postgres=# CREATE USER postgres WITH LOGIN PASSWORD 'postgres'    


### Setup local redis server
You can install redis using [the project's Quickstart instructions](https://redis.io/topics/quickstart).

Or, if you're on macOS with homebrew, you can simply run

    brew install redis

Once you've got redis installed on your system, start the local server in the background with

    redis-server  --daemonize yes


### Run database migrations
Detect changes to `models.py` and generate a timestamped migration file. To do so create a folder named ```versions``` inside ```alembic``` folder and run the following:

    alembic revision --autogenerate

Once you've looked over the generated migrations file, apply the migration to the database

    alembic upgrade head

Note that you will need to run both of these commands once at initial setup to get your database setup.

You can roll back a migration using

    alembic downgrade -1

### Proxies
A list of proxy IPs and ports should be stored in `input/proxies.txt`.

They should be listed one per line, in the following format:

    {ip_address}:{port}

If proxies are required to run the scrape -- meaning the scrape should stop if no proxies are available -- then you should set the following environment variable:

    export PROXIES_REQUIRED="true"

Note that once the target site identifies a proxy and blocks it, that proxy will be removed from the in-memory proxy list for that scrape (it is not removed from the proxies file). This means that a scrape may start out with a full list of proxies but end up grinding to a halt if requests are made too frequently and proxies started to get detected by the target site and removed from the proxy list until none are left.

From experience running this scrape, with 50 proxies you should not use more than 4 workers running requests at the same time.

If proxies are not required to scrape (ie due to low-volume local testing) you can disable that check by setting

    export PROXIES_REQUIRED="false"


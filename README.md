# Archaeological Survey Location Collector version 2 Backend

This is the Django backend for the mobile app [aslcv](https://github.com/ggetzie/aslcv2)

## Setup

There are two instances of this backend currently in use, one in production and one for testing.

To set up a local instance for development, follow these steps:

### Set up the databases.

Yes, plural, there are two databases. They are both in Postgres. One contains django specific information for the app - usernames, passwords, migrations and the like. This database is managed by django. It should be named by the `DJANGO_DB` variable in the .env file. The other database is **NOT** managed by django. It is maintained separately and used by other applications. This contains all of the user uploaded data about the archaeological finds. It should be named by the `ARCHAEOLOGY_DB` variable in the .env.

Since these already exist, obtain dumps of the databases via `pg_dump`. Then to set up locally:

#### Create users

The databases expect two users to exist. Name them `dbrw` and `dbro`. `dbrw` is the read-write user. It will also own both databases. Store that username and password in the .env file in the variables `ARCHAEOLOGY_DB_USER`, `ARCHAEOLOGY_DB_PW`, and `aslcv2_DB_PW`. Create both users in postgres with the `CREATE USER` command.

#### Create the databases in postgres.

The `DJANGO_DB` is fairly straightforward. Create an empty database in postgres with the command: `CREATE DATABASE aslcv2_be OWNER dbrw`. Then import the dump with `psql aslcv2_be < /path/to/aslcv2_be.pgsql`.

The `ARCHAEOLOGY_DB` is a little trickier because it required PostGIS.

First make sure postgis is installed. On Ubuntu run `sudo apt install postgis postgresql-14-postgis-3`. Replace "14" with the version of postgresql you're using.

Then in postgres:

```
CREATE USER dbro;
CREATE DATABASE archaeology OWNER dbrw;
CREATE SCHEMA postgis; # the archaeology database expects postgis to be installed in this schema
CREATE EXTENSION postgis WITH SCHEMA postgis;
```

Then you should be able to import the data from the .pgsql file without any errors.

```
psql archaeology < /path/to/archaeology.pgsql
```

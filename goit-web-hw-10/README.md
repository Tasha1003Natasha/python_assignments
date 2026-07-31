# Quotes to Scrape

Django web application for viewing quotes, authors, and tags. The project uses
PostgreSQL as the main database and includes user registration/login plus a
custom command for migrating authors and quotes from MongoDB to PostgreSQL.

## Features

- View all quotes without authentication.
- View author detail pages without authentication.
- Register a new user.
- Log in and log out.
- Add a new author only as an authenticated user.
- Add a new quote with selected author and tags only as an authenticated user.
- Migrate authors, quotes, and tags from MongoDB to PostgreSQL.

## Tech Stack

- Python
- Django
- PostgreSQL
- MongoDB
- PyMongo
- Docker Compose for PostgreSQL

## Environment Variables

Create a `.env` file in the project root using `.env.example` as a template:

```env
POSTGRES_PASSWORD=your_password
POSTGRES_USER=goit_user
POSTGRES_DB=goit_quotes_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=quotes
```

`MONGO_URI` and `MONGO_DB` are used by the MongoDB migration command.

## Installation

Activate the virtual environment:

```bash
source venv/bin/activate
```

Install dependencies if needed:

```bash
pip install Django psycopg psycopg-binary python-dotenv pymongo
```

## PostgreSQL

Start PostgreSQL with Docker Compose:

```bash
docker compose up -d
```

Apply Django migrations:

```bash
cd quotes_project
python manage.py migrate
```

## MongoDB to PostgreSQL Migration

The project has a custom Django management command:

```bash
python manage.py migrate_mongo
```

By default it uses:

```text
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=quotes
```

You can also pass values directly:

```bash
python manage.py migrate_mongo --mongo-uri mongodb://localhost:27017/ --mongo-db quotes
```

The command reads MongoDB collections:

- `authors`
- `quotes`

and creates or updates PostgreSQL records in:

- `Author`
- `Quote`
- `Tag`

## Load Data from JSON

There is also a helper command for loading seed data from JSON files:

```bash
python manage.py load_quotes
```

It reads:

- `utils/authors.json`
- `utils/qoutes.json`

## Run Server

From the `quotes_project` directory:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Main URLs

- `/` - quotes list
- `/users/signup/` - registration
- `/users/login/` - login
- `/users/logout/` - logout
- `/author/<id>/` - author detail
- `/author/` - add author, login required
- `/quote/` - add quote, login required
- `/tag/<tag_name>/` - quotes by tag

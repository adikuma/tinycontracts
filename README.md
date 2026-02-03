# tinycontracts

Turn JSON, CSV, and Parquet files into REST APIs instantly.

## Install

```bash
pip install tinycontracts
```

## Usage

```bash
tc ./data
```

Or with options:

```bash
tc ./data --port 8000 --host 0.0.0.0
```

## Example

Given this structure:
```
data/
  users.json
  orders.csv
  config.json
```

You get:
```
GET /users          # list all users
GET /users/1        # get user by id
GET /orders         # list all orders
GET /config         # get config

GET /_help          # api documentation
GET /_schema        # all schemas
GET /docs           # swagger ui
```

## Filtering & Pagination

```bash
# filter by field
curl "localhost:4242/users?active=true"

# pagination
curl "localhost:4242/orders?_limit=10&_offset=20"

# sorting
curl "localhost:4242/orders?_sort=-created_at"

# combine
curl "localhost:4242/orders?status=pending&_limit=5&_sort=-amount"
```

## Schema

```bash
# all schemas
curl localhost:4242/_schema

# single resource schema
curl localhost:4242/users/_schema
```

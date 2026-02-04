# tinycontracts

Turn any folder of JSON, CSV, or Parquet files into a REST API instantly.

## Install

```bash
pip install tinycontracts
```

## Usage

```bash
tc ./data
```

That's it. Your files are now API endpoints.

## Options

```bash
tc ./data -p 8000           # custom port (default: 4242)
tc ./data -H 0.0.0.0        # expose to network
tc --version                # show version
```

## Example

```
data/
  users.json     ->  GET /users
  orders.csv     ->  GET /orders
  config.json    ->  GET /config
```

## Querying

```bash
# filter
curl "localhost:4242/users?active=true"

# pagination
curl "localhost:4242/orders?_limit=10&_offset=20"

# sort
curl "localhost:4242/orders?_sort=-created_at"

# combine
curl "localhost:4242/orders?status=pending&_limit=5"
```

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `/{resource}` | List all rows |
| `/{resource}/{id}` | Get by ID |
| `/{resource}/_schema` | JSON schema |
| `/_help` | API documentation |
| `/_schema` | All schemas |
| `/docs` | Swagger UI |

# routes.py - dynamic route generation
import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse


def create_discovery_routes(
    app: FastAPI, resources: dict[str, pd.DataFrame], schemas: dict[str, dict]
):
    @app.get("/")
    def list_resources():
        return {"resources": list(resources.keys())}

    @app.get("/_schema")
    def get_all_schemas():
        return schemas

    @app.get("/_help", response_class=PlainTextResponse)
    def get_help():
        resource_list = "\n".join(f"  - /{name}" for name in resources.keys())
        return f"""tinycontracts api

        resources:
        {resource_list}

        endpoints per resource:
        GET /{{resource}}          list all rows
        GET /{{resource}}/{{id}}      get row by id
        GET /{{resource}}/_schema  get schema
        GET /{{resource}}/_sample  get random sample

        query parameters:
        ?field=value   filter by field
        ?_limit=N      limit results (default 100)
        ?_offset=N     skip first N results
        ?_sort=field   sort ascending
        ?_sort=-field  sort descending
        ?n=N           sample size (for /_sample)

        global endpoints:
        GET /          list all resources
        GET /_schema   all schemas
        GET /_help     this help text
        """


def create_resource_routes(app: FastAPI, name: str, df: pd.DataFrame, schema: dict):
    # store df in closure
    data = df.copy()

    @app.get(f"/{name}/_schema")
    def get_schema():
        return schema

    @app.get(f"/{name}/_sample")
    def get_sample(n: int = 10):
        sample_size = min(n, len(data))
        return data.sample(n=sample_size).to_dict(orient="records")

    @app.get(f"/{name}/{{row_id}}")
    def get_row(row_id: str):
        # try to find id column
        id_col = None
        if "id" in data.columns:
            id_col = "id"
        elif len(data.columns) > 0:
            id_col = data.columns[0]

        if id_col is None:
            raise HTTPException(status_code=400, detail="no id column found")

        # try to match as int or string
        try:
            row_id_int = int(row_id)
            match = data[data[id_col] == row_id_int]
        except ValueError:
            match = data[data[id_col] == row_id]

        if len(match) == 0:
            raise HTTPException(status_code=404, detail="row not found")

        return match.iloc[0].to_dict()

    @app.get(f"/{name}")
    def list_rows(
        request: Request,
        _limit: int = Query(100, alias="_limit"),
        _offset: int = Query(0, alias="_offset"),
        _sort: str = Query(None, alias="_sort"),
    ):
        result = data.copy()

        # filter by query params (exclude special params)
        special_params = {"_limit", "_offset", "_sort"}
        for key, value in request.query_params.items():
            if key not in special_params and key in result.columns:
                # try to cast value to column type
                try:
                    if result[key].dtype == "int64":
                        value = int(value)
                    elif result[key].dtype == "float64":
                        value = float(value)
                    elif result[key].dtype == "bool":
                        value = value.lower() in ("true", "1", "yes")
                except ValueError:
                    pass
                result = result[result[key] == value]

        # sort
        if _sort:
            descending = _sort.startswith("-")
            col = _sort.lstrip("-")
            if col in result.columns:
                result = result.sort_values(col, ascending=not descending)

        # offset and limit
        result = result.iloc[_offset : _offset + _limit]

        return result.to_dict(orient="records")

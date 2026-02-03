# server.py - fastapi app factory
from pathlib import Path

from fastapi import FastAPI

from tinycontracts.loader import load_folder
from tinycontracts.routes import create_discovery_routes, create_resource_routes
from tinycontracts.schema import infer_schema


def create_app(folder: Path) -> FastAPI:
    resources = load_folder(folder)
    schemas = {name: infer_schema(df) for name, df in resources.items()}

    app = FastAPI(title="tinycontracts", docs_url="/docs", redoc_url=None)
    app.state.resources = resources
    app.state.schemas = schemas

    create_discovery_routes(app, resources, schemas)

    for name, df in resources.items():
        create_resource_routes(app, name, df, schemas[name])

    return app

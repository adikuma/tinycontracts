# server.py - fastapi app factory
from pathlib import Path

from fastapi import FastAPI

from src.loader import load_folder
from src.routes import create_discovery_routes, create_resource_routes
from src.schema import infer_schema


def create_app(folder: Path) -> FastAPI:
    resources = load_folder(folder)
    # infer schema for each resource
    schemas = {name: infer_schema(df) for name, df in resources.items()}
    # define app
    app = FastAPI(title="tinycontracts")
    # add discovery routes
    create_discovery_routes(app, resources, schemas)

    # add resource routes for each
    for name, df in resources.items():
        create_resource_routes(app, name, df, schemas[name])

    return app

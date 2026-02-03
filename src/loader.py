# loader.py - load json/csv/parquet files
import json
from pathlib import Path

import pandas as pd


def load_file(path: Path) -> pd.DataFrame:
    if path.suffix == ".json":
        data = json.load(path.open())
        # handle singleton (single object) vs collection (array)
        if isinstance(data, dict):
            data = [data]
        return pd.DataFrame(data)
    elif path.suffix == ".csv":
        return pd.read_csv(path)
    elif path.suffix == ".parquet":
        return pd.read_parquet(path)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")


def load_folder(folder: Path) -> dict[str, pd.DataFrame]:
    resources = {}
    for path in folder.glob("*"):
        if path.suffix in [".json", ".csv", ".parquet"]:
            name = path.stem  # filename without extension
            resources[name] = load_file(path)
    return resources

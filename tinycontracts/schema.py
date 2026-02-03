# schema.py - infer schema from dataframes
import pandas as pd


def infer_column_schema(series: pd.Series) -> str:
    dtype_str = str(series.dtype)

    if dtype_str in ("object", "str", "string"):
        return "string"
    elif "int" in dtype_str:
        return "integer"
    elif "float" in dtype_str:
        return "number"
    elif dtype_str == "bool":
        return "boolean"
    else:
        # fallback to string for unknown types
        return "string"


def infer_schema(df: pd.DataFrame) -> dict:
    properties = {}
    for column in df.columns:
        properties[column] = {"type": infer_column_schema(df[column])}
    return {"type": "object", "properties": properties}

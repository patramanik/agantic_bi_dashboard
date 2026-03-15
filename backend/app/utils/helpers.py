import pandas as pd
import json
from typing import Any

def to_json_safe_dict(data: Any) -> Any:
    """Helper to convert any data with Pandas/NumPy types to JSON-safe Python objects."""
    if isinstance(data, pd.DataFrame):
        return json.loads(data.to_json(orient='records', date_format='iso'))
    elif isinstance(data, dict):
        return {k: to_json_safe_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [to_json_safe_dict(i) for i in data]
    return data

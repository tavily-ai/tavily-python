import tiktoken
import json
from typing import Sequence, List, Dict, Union
from .config import DEFAULT_MODEL_ENCODING, DEFAULT_MAX_TOKENS


def resolve_output_schema(output_schema) -> Union[dict, None]:
    """Convert a Pydantic BaseModel subclass to a Tavily-compatible JSON schema dict.

    Tavily's API only accepts 'properties' and 'required' at the top level.
    This strips the full Pydantic JSON schema down to those keys and resolves
    any $ref/$defs references inline so nested models are inlined.

    Plain dicts are passed through unchanged. If pydantic is not installed
    and a non-dict is passed, it is returned as-is.
    """
    if output_schema is None:
        return None
    try:
        from pydantic import BaseModel
        if isinstance(output_schema, type) and issubclass(output_schema, BaseModel):
            schema = output_schema.model_json_schema()
            defs = schema.get("$defs", {})

            def _resolve(obj):
                if isinstance(obj, dict):
                    if "$ref" in obj:
                        ref_name = obj["$ref"].split("/")[-1]
                        return _resolve(defs[ref_name])
                    return {k: _resolve(v) for k, v in obj.items() if k != "title"}
                if isinstance(obj, list):
                    return [_resolve(i) for i in obj]
                return obj

            resolved = _resolve(schema)
            return {k: resolved[k] for k in ("properties", "required") if k in resolved}
    except ImportError:
        pass
    return output_schema


def get_total_tokens_from_string(string: str, encoding_name: str = DEFAULT_MODEL_ENCODING) -> int:
    """
        Get total amount of tokens from string using the specified encoding (based on openai compute)
    """
    encoding = tiktoken.encoding_for_model(encoding_name)
    tokens = encoding.encode(string)
    return len(tokens)

def get_max_items_from_list(data: Sequence[dict], max_tokens: int = DEFAULT_MAX_TOKENS) -> List[Dict[str,str]]:
    """
        Get max items from list of items based on defined max tokens (based on openai compute)
    """
    result = []
    current_tokens = 0
    for item in data:
        item_str = json.dumps(item)
        new_total_tokens = current_tokens + get_total_tokens_from_string(item_str)
        if new_total_tokens > max_tokens:
            break
        else:
            result.append(item)
            current_tokens = new_total_tokens
    return result

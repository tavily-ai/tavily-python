import tiktoken
import json
from typing import Any, List, Sequence, Dict, Tuple
from .config import DEFAULT_MODEL_ENCODING, DEFAULT_MAX_TOKENS


def _merge_duplicate_json_keys(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    """
    object_pairs_hook for json.loads that merges repeated object keys whose
    values are lists instead of silently keeping only the last one.

    The API can occasionally emit a JSON object with a key repeated more than
    once (e.g. two separate "images" entries). Python's default dict-building
    behavior keeps only the last occurrence, discarding the earlier data with
    no warning. When every occurrence of a repeated key is a list, concatenate
    them; any other repeated key keeps the standard last-value-wins behavior.
    """
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result and isinstance(result[key], list) and isinstance(value, list):
            result[key] = result[key] + value
        else:
            result[key] = value
    return result


def parse_json_response(text: str):
    """
    Parse an API response body, merging duplicate object keys that hold lists
    (see ``_merge_duplicate_json_keys``) instead of dropping data silently.
    """
    return json.loads(text, object_pairs_hook=_merge_duplicate_json_keys)


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

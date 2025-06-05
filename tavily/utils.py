import tiktoken
import json
from typing import Sequence, List, Dict, Any, TypeVar
from .config import DEFAULT_MODEL_ENCODING, DEFAULT_MAX_TOKENS

T = TypeVar('T', bound=Dict[str, Any])


def get_total_tokens_from_string(string: str, encoding_name: str = DEFAULT_MODEL_ENCODING) -> int:
    """
        Get total amount of tokens from string using the specified encoding (based on openai compute)
    """
    encoding = tiktoken.encoding_for_model(encoding_name)
    tokens = encoding.encode(string)
    return len(tokens)


def get_max_tokens_from_string(string: str, max_tokens: int, encoding_name: str = DEFAULT_MODEL_ENCODING) -> str:
    """
        Extract max tokens from string using the specified encoding (based on openai compute)
    """
    encoding = tiktoken.encoding_for_model(encoding_name)
    tokens = encoding.encode(string)
    token_bytes = [encoding.decode_single_token_bytes(token) for token in tokens[:max_tokens]]
    return b"".join(token_bytes).decode()


def get_max_items_from_list(data: Sequence[T], max_tokens: int = DEFAULT_MAX_TOKENS) -> List[T]:
    """
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

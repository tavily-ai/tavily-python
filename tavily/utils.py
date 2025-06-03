"""
Utility functions for the Tavily API client.

This module provides utility functions for token counting and content management
when working with the Tavily API. These functions help manage token limits and
content truncation for API requests.

The utilities include:
- Token counting for strings
- Content truncation based on token limits
- List item filtering based on token limits
"""

import json
from typing import Dict, List, Sequence

import tiktoken

from .config import DEFAULT_MAX_TOKENS, DEFAULT_MODEL_ENCODING


def get_total_tokens_from_string(
    string: str, encoding_name: str = DEFAULT_MODEL_ENCODING
) -> int:
    """Calculate the total number of tokens in a string using the specified encoding.

    This function uses the tiktoken library to count tokens in a string, which is
    useful for managing API request limits and content length.

    Args:
        string (str): The input string to count tokens for.
        encoding_name (str): The name of the encoding model to use for tokenization.
            Defaults to the value specified in DEFAULT_MODEL_ENCODING.

    Returns:
        int: The total number of tokens in the input string.

    Example:
        >>> get_total_tokens_from_string("Hello, world!")
        4
    """
    encoding = tiktoken.encoding_for_model(encoding_name)
    tokens = encoding.encode(string)
    return len(tokens)


def get_max_tokens_from_string(
    string: str, max_tokens: int, encoding_name: str = DEFAULT_MODEL_ENCODING
) -> str:
    """Extract a substring containing at most the specified number of tokens.

    This function truncates a string to contain at most the specified number of
    tokens, ensuring that the truncation happens at token boundaries.

    Args:
        string (str): The input string to truncate.
        max_tokens (int): The maximum number of tokens to include in the result.
        encoding_name (str): The name of the encoding model to use for tokenization.
            Defaults to the value specified in DEFAULT_MODEL_ENCODING.

    Returns:
        str: A substring containing at most max_tokens tokens.

    Example:
        >>> get_max_tokens_from_string("Hello, world! How are you?", max_tokens=3)
        "Hello, world"
    """
    encoding = tiktoken.encoding_for_model(encoding_name)
    tokens = encoding.encode(string)
    token_bytes = [
        encoding.decode_single_token_bytes(token) for token in tokens[:max_tokens]
    ]
    return b"".join(token_bytes).decode()


def get_max_items_from_list(
    data: Sequence[dict], max_tokens: int = DEFAULT_MAX_TOKENS
) -> List[Dict[str, str]]:
    """Filter a list of dictionaries to include at most the specified number of tokens.

    This function processes a list of dictionaries and returns a subset that fits
    within the specified token limit. It's useful for managing API request sizes
    when working with lists of items.

    Args:
        data (Sequence[dict]): The list of dictionaries to filter.
        max_tokens (int): The maximum number of tokens allowed in the result.
            Defaults to the value specified in DEFAULT_MAX_TOKENS.

    Returns:
        List[Dict[str, str]]: A list of dictionaries that fit within the token limit.

    Example:
        >>> items = [{"text": "Hello"}, {"text": "World"}]
        >>> get_max_items_from_list(items, max_tokens=8)
        [{"text": "Hello"}]
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

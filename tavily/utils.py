import tiktoken
import json
import random
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Sequence, List, Dict, Optional
from .config import DEFAULT_MODEL_ENCODING, DEFAULT_MAX_TOKENS


def get_total_tokens_from_string(string: str, encoding_name: str = DEFAULT_MODEL_ENCODING) -> int:
    """
        Get total amount of tokens from string using the specified encoding (based on openai compute)
    """
    encoding = tiktoken.encoding_for_model(encoding_name)
    tokens = encoding.encode(string)
    return len(tokens)

def parse_retry_after(headers) -> Optional[float]:
    """
        Parse an HTTP ``Retry-After`` header value into seconds.

        Supports both the integer-seconds and HTTP-date forms. Returns None
        when the header is absent or cannot be parsed.
    """
    if not headers:
        return None
    raw = None
    for name in ("Retry-After", "retry-after"):
        try:
            raw = headers.get(name)
        except Exception:
            return None
        if raw:
            break
    if raw is None:
        return None
    raw = str(raw).strip()
    if not raw:
        return None
    try:
        return max(0.0, float(raw))
    except ValueError:
        pass
    try:
        parsed = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        return None
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return max(0.0, (parsed - datetime.now(timezone.utc)).total_seconds())

def retry_delay(attempt: int, headers=None) -> float:
    """
        Seconds to wait before retry attempt ``attempt`` (1-based).

        Honors ``Retry-After`` when the server sent one; otherwise uses
        exponential backoff with full jitter, capped at 60 seconds.
    """
    retry_after = parse_retry_after(headers)
    if retry_after is not None:
        return retry_after
    backoff = min(60.0, 1.0 * (2 ** (attempt - 1)))
    return random.uniform(0, backoff)

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

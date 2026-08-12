import tiktoken
import json
from urllib.parse import urlparse
from typing import Sequence, List, Dict, Optional
from .config import DEFAULT_MODEL_ENCODING, DEFAULT_MAX_TOKENS


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


def filter_results_by_domains(
    results: Sequence[dict], include_domains: Optional[Sequence[str]] = None
) -> List[dict]:
    """Keep only results whose host matches an included domain or its subdomain."""
    if not include_domains:
        return list(results)

    domains = {
        domain.strip().lower().rstrip(".")
        for domain in include_domains
        if isinstance(domain, str) and domain.strip()
    }
    if not domains:
        return list(results)

    filtered_results = []
    for result in results:
        if not isinstance(result, dict):
            continue
        try:
            hostname = urlparse(result.get("url", "")).hostname
        except (TypeError, ValueError):
            continue
        if hostname is None:
            continue
        hostname = hostname.lower().rstrip(".")
        if any(hostname == domain or hostname.endswith(f".{domain}") for domain in domains):
            filtered_results.append(result)

    return filtered_results

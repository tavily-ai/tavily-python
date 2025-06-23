import tiktoken
import json
import codecs
import unicodedata
import re
from typing import Sequence, List, Dict, Any, Union
from .config import DEFAULT_MODEL_ENCODING, DEFAULT_MAX_TOKENS


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


def _is_malformed_utf8(text: str) -> bool:
    """
        Detect if text contains malformed UTF-8 encoded Chinese characters.
        Looks for patterns like '\x85¾è®¯æ' that should be proper UTF-8.
    """
    if not isinstance(text, str):
        return False
    
    # Pattern to detect hex escape sequences that might be malformed UTF-8
    hex_pattern = re.compile(r'\\x[0-9a-fA-F]{2}')
    
    # Check if text contains hex escape sequences
    if hex_pattern.search(text):
        return True
    
    # Check for mixed encoding patterns (valid UTF-8 mixed with escape sequences)
    # This catches cases where some Chinese characters are properly encoded
    # while others are escaped
    chinese_char_pattern = re.compile(r'[\u4e00-\u9fff]')
    has_chinese = chinese_char_pattern.search(text)
    has_hex_escapes = hex_pattern.search(text)
    
    return has_chinese and has_hex_escapes


def _fix_utf8_encoding(text: str) -> str:
    """
        Fix malformed UTF-8 encoding in text content.
        Handles common encoding issues with Chinese characters.
    """
    if not isinstance(text, str) or not _is_malformed_utf8(text):
        return text
    
    try:
        # First, try to decode hex escape sequences
        # This handles cases like '\x85¾è®¯æ'
        fixed_text = text
        
        # Pattern to find hex escape sequences
        hex_pattern = re.compile(r'\\x([0-9a-fA-F]{2})')
        
        def hex_replacer(match):
            try:
                hex_value = int(match.group(1), 16)
                return chr(hex_value)
            except (ValueError, OverflowError):
                return match.group(0)  # Return original if conversion fails
        
        # Replace hex escape sequences with actual characters
        fixed_text = hex_pattern.sub(hex_replacer, fixed_text)
        
        # Try to encode as latin-1 then decode as utf-8
        # This handles double-encoding issues
        try:
            if isinstance(fixed_text, str):
                # Convert to bytes using latin-1, then decode as utf-8
                byte_data = fixed_text.encode('latin-1')
                fixed_text = byte_data.decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass  # If this fails, continue with the hex-fixed version
        
        # Normalize Unicode characters
        fixed_text = unicodedata.normalize('NFC', fixed_text)
        
        return fixed_text
        
    except Exception:
        # If all else fails, return the original text
        # Better to have malformed text than crash the application
        return text


def normalize_content_encoding(data: Union[Dict[str, Any], List[Dict[str, Any]], str]) -> Union[Dict[str, Any], List[Dict[str, Any]], str]:
    """
        Normalize UTF-8 encoding in content fields of API response data.
        Recursively processes dictionaries and lists to fix encoding issues.
        
        Args:
            data: API response data that may contain malformed UTF-8 content
            
        Returns:
            Data with normalized UTF-8 encoding
    """
    if isinstance(data, dict):
        normalized_data = {}
        for key, value in data.items():
            if key == 'content' and isinstance(value, str):
                # Apply UTF-8 normalization to content fields
                normalized_data[key] = _fix_utf8_encoding(value)
            elif key in ['title', 'raw_content'] and isinstance(value, str):
                # Also normalize title and raw_content fields that may contain text
                normalized_data[key] = _fix_utf8_encoding(value)
            elif isinstance(value, (dict, list)):
                # Recursively process nested structures
                normalized_data[key] = normalize_content_encoding(value)
            else:
                normalized_data[key] = value
        return normalized_data
    
    elif isinstance(data, list):
        return [normalize_content_encoding(item) for item in data]
    
    elif isinstance(data, str):
        return _fix_utf8_encoding(data)
    
    else:
        return data

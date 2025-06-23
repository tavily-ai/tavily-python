#!/usr/bin/env python3
"""
UTF-8 Encoding Fix Demonstration

This script demonstrates how the Tavily Python client now handles
UTF-8 encoding issues with Chinese characters in API responses.

GitHub Issue #93: When search_model is "advanced" and search query is chinese, 
the encoding of the content field in the output result is sometimes not utf-8
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# NOTE: In production, use: from tavily import TavilyClient
# from tavily import TavilyClient
# from tavily.async_tavily import AsyncTavilyClient
import asyncio


def demonstrate_utf8_fix():
    """Demonstrate the UTF-8 encoding fix with examples"""
    
    print("Tavily Python UTF-8 Encoding Fix Demonstration")
    print("=" * 55)
    print()
    
    print("GitHub Issue #93 Solution:")
    print("When search_depth='advanced' with Chinese queries, content")
    print("fields now automatically normalize malformed UTF-8 encoding.")
    print()
    
    # Example 1: Client with UTF-8 normalization enabled (default)
    print("1. Client with UTF-8 normalization (default behavior):")
    print("   client = TavilyClient(api_key='your-key')  # normalize_content=True by default")
    print("   result = client.search('腾讯', search_depth='advanced')")
    print("   # Chinese characters in 'content' field will be properly displayed")
    print()
    
    # Example 2: Client with UTF-8 normalization disabled
    print("2. Client with UTF-8 normalization disabled:")
    print("   client = TavilyClient(api_key='your-key', normalize_content=False)")
    print("   result = client.search('腾讯', search_depth='advanced')")
    print("   # Content may contain escape sequences like '\\x85¾è®¯æ'")
    print()
    
    # Example 3: Async client
    print("3. Async client (also supports UTF-8 normalization):")
    print("   client = AsyncTavilyClient(api_key='your-key')  # normalize_content=True by default")
    print("   result = await client.search('腾讯', search_depth='advanced')")
    print("   # Chinese characters properly normalized in async operations too")
    print()
    
    print("Before Fix (GitHub Issue #93):")
    print("─" * 30)
    malformed_example = {
        'url': 'https://apps.apple.com/cn/app/腾讯文档/id1370780836',
        'title': 'App Store 上的"腾讯文档"',
        'content': 'è\\x85¾è®¯æ\\x96\\x87â\\x80ªæ¡£â\\x80¬\\n 4+\\n\\nå\\x8f¯å¤\\x9aäººå®\\x9eæ\\x97¶å\\x8d\\x8fä½\\x9cç\\x9a\\x84å\\x9c¨çº¿æ\\x96\\x87â\\x80ªæ¡£â\\x80¬',
        'score': 0.48294178
    }
    
    print(f"Content: {malformed_example['content'][:50]}...")
    print("^ Contains hex escape sequences instead of proper Chinese characters")
    print()
    
    print("After Fix:")
    print("─" * 10)
    # Import and use our normalization function
    try:
        from tavily.utils import normalize_content_encoding
    except ImportError:
        # Fallback for demo purposes - in production this won't be needed
        print("Note: Running in demo mode without full package installation")
        return
    
    fixed_example = normalize_content_encoding(malformed_example)
    print(f"Content: {fixed_example['content'][:50]}...")
    print("^ Properly displays Chinese characters: 腾讯文档")
    print()
    
    print("Technical Details:")
    print("─" * 17)
    print("• Detects malformed UTF-8 patterns (hex escape sequences)")
    print("• Converts escape sequences to proper Unicode characters")
    print("• Handles double-encoding issues common with Chinese text")
    print("• Normalizes Unicode to NFC form for consistent display")
    print("• Processes content, title, and raw_content fields recursively")
    print("• Preserves all other response data unchanged")
    print("• Configurable via normalize_content parameter")
    print()
    
    print("Supported Methods:")
    print("─" * 17)
    print("• search() - All search operations with Chinese queries")
    print("• extract() - Content extraction from Chinese websites")
    print("• crawl() - Website crawling with Chinese content")
    print("• map() - Website mapping with Chinese content")
    print("• Both sync (TavilyClient) and async (AsyncTavilyClient)")
    print()
    
    print("Usage Examples:")
    print("─" * 14)
    print("""
# Basic usage (UTF-8 normalization enabled by default)
from tavily import TavilyClient

client = TavilyClient(api_key="your-api-key")
result = client.search("腾讯", search_depth="advanced")

# Content field will display Chinese characters properly
for item in result['results']:
    print(f"Title: {item['title']}")
    print(f"Content: {item['content'][:100]}...")
    
# Disable UTF-8 normalization if needed
client = TavilyClient(api_key="your-api-key", normalize_content=False)

# Async usage
import asyncio
from tavily.async_tavily import AsyncTavilyClient

async def search_chinese():
    client = AsyncTavilyClient(api_key="your-api-key")
    result = await client.search("腾讯文档", search_depth="advanced")
    return result

# Run async search
result = asyncio.run(search_chinese())
""")
    
    print("=" * 55)
    print("UTF-8 encoding issue resolved! ✅")
    print("Chinese characters in API responses now display correctly.")


if __name__ == "__main__":
    demonstrate_utf8_fix() 
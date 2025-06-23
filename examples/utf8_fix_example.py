#!/usr/bin/env python3
"""
UTF-8 Encoding Fix Example for GitHub Issue #93

This example demonstrates the solution for malformed UTF-8 encoding
in Chinese content when using search_depth="advanced".

Problem: Chinese characters appeared as escape sequences like '\x85¾è®¯æ'
Solution: Automatic UTF-8 content normalization in the client
"""

import re
import unicodedata


def demonstrate_utf8_fix():
    """Show before/after examples of the UTF-8 encoding fix"""
    
    print("🔧 Tavily Python UTF-8 Encoding Fix")
    print("=" * 50)
    print()
    
    # Real example from GitHub Issue #93
    print("📋 GitHub Issue #93 Example:")
    print("-" * 30)
    
    # Before: Malformed content from API response
    malformed_result = {
        'url': 'https://apps.apple.com/cn/app/腾讯文档/id1370780836',
        'title': 'App Store 上的"腾讯文档"',
        'content': 'è\\x85¾è®¯æ\\x96\\x87â\\x80ªæ¡£â\\x80¬\\n 4+\\n\\nå\\x8f¯å¤\\x9aäººå®\\x9eæ\\x97¶å\\x8d\\x8fä½\\x9cç\\x9a\\x84å\\x9c¨çº¿æ\\x96\\x87â\\x80ªæ¡£â\\x80¬',
        'score': 0.48294178
    }
    
    print("❌ BEFORE (malformed UTF-8):")
    print(f"   Content: {malformed_result['content'][:60]}...")
    print("   ^ Contains hex escape sequences instead of Chinese text")
    print()
    
    # Apply the fix (simplified version of our normalization)
    def fix_utf8_content(text):
        if not isinstance(text, str):
            return text
        
        # Convert hex escape sequences to characters
        hex_pattern = re.compile(r'\\x([0-9a-fA-F]{2})')
        def hex_replacer(match):
            try:
                return chr(int(match.group(1), 16))
            except (ValueError, OverflowError):
                return match.group(0)
        
        fixed = hex_pattern.sub(hex_replacer, text)
        
        # Handle double-encoding
        try:
            fixed = fixed.encode('latin-1').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        
        # Normalize Unicode
        return unicodedata.normalize('NFC', fixed)
    
    # Fix the content
    fixed_result = malformed_result.copy()
    fixed_result['content'] = fix_utf8_content(malformed_result['content'])
    
    print("✅ AFTER (fixed UTF-8):")
    print(f"   Content: {fixed_result['content'][:60]}...")
    print("   ^ Properly displays Chinese characters!")
    print()
    
    print("🔍 Technical Details:")
    print("-" * 20)
    print("• Detects hex escape patterns like '\\x85'")
    print("• Converts to proper Unicode characters")
    print("• Handles double-encoding issues")
    print("• Normalizes to NFC Unicode form")
    print("• Works with all API methods (search, extract, crawl, map)")
    print()
    
    print("💻 Usage in Your Code:")
    print("-" * 22)
    print("""
# UTF-8 normalization is enabled by default
from tavily import TavilyClient

client = TavilyClient(api_key="your-api-key")
result = client.search("腾讯", search_depth="advanced")

# Chinese characters now display correctly!
for item in result['results']:
    print(f"Title: {item['title']}")
    print(f"Content: {item['content']}")
    
# Disable normalization if needed (not recommended)
client = TavilyClient(api_key="your-api-key", normalize_content=False)

# Also works with async client
from tavily.async_tavily import AsyncTavilyClient
async_client = AsyncTavilyClient(api_key="your-api-key")
result = await async_client.search("腾讯文档", search_depth="advanced")
""")
    
    print("🎯 Key Benefits:")
    print("-" * 15)
    print("• ✅ Chinese characters display correctly")
    print("• ✅ Backward compatible (enabled by default)")
    print("• ✅ Configurable (can be disabled)")
    print("• ✅ Works with both sync and async clients")
    print("• ✅ Handles all content fields (content, title, raw_content)")
    print("• ✅ Zero performance impact on non-Chinese content")
    print()
    
    print("=" * 50)
    print("🎉 GitHub Issue #93 RESOLVED!")
    print("Chinese search results now display properly ✨")


if __name__ == "__main__":
    demonstrate_utf8_fix() 
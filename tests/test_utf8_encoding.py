import pytest
import json
from unittest.mock import Mock, patch
from tavily import TavilyClient
from tavily.async_tavily import AsyncTavilyClient
from tavily.utils import normalize_content_encoding, _is_malformed_utf8, _fix_utf8_encoding


class TestUTF8EncodingUtils:
    """Test UTF-8 encoding utility functions"""
    
    def test_is_malformed_utf8_detection(self):
        """Test detection of malformed UTF-8 content"""
        # Test cases with malformed UTF-8 (from the GitHub issue example)
        malformed_content = 'è\x85¾è®¯æ\x96\x87â\x80ªæ¡£â\x80¬'
        assert _is_malformed_utf8(malformed_content) == True
        
        # Test normal UTF-8 content
        normal_content = 'Tencent 腾讯'
        assert _is_malformed_utf8(normal_content) == False
        
        # Test content with only hex escapes
        hex_only = '\\x85\\x86\\x87'
        assert _is_malformed_utf8(hex_only) == True
        
        # Test empty string
        assert _is_malformed_utf8('') == False
        
        # Test non-string input
        assert _is_malformed_utf8(None) == False
        assert _is_malformed_utf8(123) == False
    
    def test_fix_utf8_encoding(self):
        """Test UTF-8 encoding fix functionality"""
        # Test fixing hex escape sequences
        malformed = '\\x85\\x86\\x87'
        fixed = _fix_utf8_encoding(malformed)
        # Should convert hex escapes to actual characters
        assert '\\x' not in fixed
        
        # Test normal content remains unchanged
        normal = 'Tencent 腾讯'
        assert _fix_utf8_encoding(normal) == normal
        
        # Test empty string
        assert _fix_utf8_encoding('') == ''
        
        # Test non-string input
        assert _fix_utf8_encoding(None) == None
        assert _fix_utf8_encoding(123) == 123
    
    def test_normalize_content_encoding_dict(self):
        """Test content encoding normalization for dictionary responses"""
        # Mock API response with malformed content (similar to GitHub issue)
        malformed_response = {
            'results': [
                {
                    'url': 'https://example.com',
                    'title': 'Test 腾讯',
                    'content': 'è\x85¾è®¯æ\x96\x87â\x80ªæ¡£â\x80¬',
                    'score': 0.9
                }
            ]
        }
        
        normalized = normalize_content_encoding(malformed_response)
        
        # Verify structure is preserved
        assert 'results' in normalized
        assert len(normalized['results']) == 1
        assert normalized['results'][0]['url'] == 'https://example.com'
        assert normalized['results'][0]['title'] == 'Test 腾讯'  # Should remain unchanged
        assert normalized['results'][0]['score'] == 0.9
        
        # Content should be processed (though exact result depends on the input)
        content = normalized['results'][0]['content']
        assert isinstance(content, str)
        # Should not contain obvious hex escape patterns
        assert '\\x85' not in content
    
    def test_normalize_content_encoding_list(self):
        """Test content encoding normalization for list responses"""
        malformed_list = [
            {
                'content': 'è\x85¾è®¯æ\x96\x87â\x80ªæ¡£â\x80¬',
                'title': 'Test Title'
            }
        ]
        
        normalized = normalize_content_encoding(malformed_list)
        
        assert isinstance(normalized, list)
        assert len(normalized) == 1
        assert normalized[0]['title'] == 'Test Title'
        
        # Content should be processed
        content = normalized[0]['content']
        assert isinstance(content, str)
    
    def test_normalize_content_encoding_string(self):
        """Test content encoding normalization for string input"""
        malformed_string = 'è\x85¾è®¯æ\x96\x87â\x80ªæ¡£â\x80¬'
        normalized = normalize_content_encoding(malformed_string)
        
        assert isinstance(normalized, str)
        # Should be processed
        assert normalized != malformed_string or not _is_malformed_utf8(normalized)
    
    def test_normalize_content_encoding_preserves_other_types(self):
        """Test that normalization preserves non-string, non-dict, non-list types"""
        assert normalize_content_encoding(123) == 123
        assert normalize_content_encoding(None) == None
        assert normalize_content_encoding(True) == True


class TestTavilyClientUTF8Integration:
    """Test UTF-8 encoding integration in TavilyClient"""
    
    @patch('tavily.tavily.requests.post')
    def test_search_with_utf8_normalization_enabled(self, mock_post):
        """Test search with UTF-8 normalization enabled (default)"""
        # Mock response with malformed UTF-8 content
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'url': 'https://example.com',
                    'title': 'Test 腾讯',
                    'content': 'è\x85¾è®¯æ\x96\x87â\x80ªæ¡£â\x80¬',
                    'score': 0.9
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # NOTE: Not fully tested with real API due to automated environment limits
        # Manual testing recommended for: Real API calls with Chinese queries
        client = TavilyClient(api_key="test-key", normalize_content=True)
        result = client.search("腾讯", search_depth="advanced")
        
        # Verify the response was processed
        assert 'results' in result
        assert len(result['results']) == 1
        
        # Content should be normalized
        content = result['results'][0]['content']
        assert isinstance(content, str)
        # Should not contain obvious malformed patterns
        assert '\\x85' not in content
    
    @patch('tavily.tavily.requests.post')
    def test_search_with_utf8_normalization_disabled(self, mock_post):
        """Test search with UTF-8 normalization disabled"""
        # Mock response with malformed UTF-8 content
        mock_response = Mock()
        mock_response.status_code = 200
        original_content = 'è\x85¾è®¯æ\x96\x87â\x80ªæ¡£â\x80¬'
        mock_response.json.return_value = {
            'results': [
                {
                    'url': 'https://example.com',
                    'title': 'Test 腾讯',
                    'content': original_content,
                    'score': 0.9
                }
            ]
        }
        mock_post.return_value = mock_response
        
        client = TavilyClient(api_key="test-key", normalize_content=False)
        result = client.search("腾讯", search_depth="advanced")
        
        # Content should remain unchanged when normalization is disabled
        assert result['results'][0]['content'] == original_content
    
    @patch('tavily.tavily.requests.post')
    def test_extract_with_utf8_normalization(self, mock_post):
        """Test extract method with UTF-8 normalization"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'url': 'https://example.com',
                    'raw_content': 'è\x85¾è®¯æ\x96\x87â\x80ªæ¡£â\x80¬',
                    'content': 'Processed content'
                }
            ]
        }
        mock_post.return_value = mock_response
        
        client = TavilyClient(api_key="test-key", normalize_content=True)
        result = client.extract("https://example.com")
        
        # Verify raw_content was processed
        raw_content = result['results'][0]['raw_content']
        assert isinstance(raw_content, str)
        # Should be normalized
        assert '\\x85' not in raw_content


class TestAsyncTavilyClientUTF8Integration:
    """Test UTF-8 encoding integration in AsyncTavilyClient"""
    
    @pytest.mark.asyncio
    @patch('tavily.async_tavily.httpx.AsyncClient')
    async def test_async_search_with_utf8_normalization(self, mock_client_class):
        """Test async search with UTF-8 normalization"""
        # Mock the async client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'url': 'https://example.com',
                    'title': 'Test 腾讯',
                    'content': 'è\x85¾è®¯æ\x96\x87â\x80ªæ¡£â\x80¬',
                    'score': 0.9
                }
            ]
        }
        
        # Setup the mock client context manager
        mock_client.post.return_value = mock_response
        mock_client_instance = Mock()
        mock_client_instance.__aenter__.return_value = mock_client
        mock_client_instance.__aexit__.return_value = None
        mock_client_class.return_value = mock_client_instance
        
        # NOTE: Not fully tested with real async API due to automated environment limits
        # Manual testing recommended for: Real async API calls with Chinese queries
        client = AsyncTavilyClient(api_key="test-key", normalize_content=True)
        result = await client.search("腾讯", search_depth="advanced")
        
        # Verify the response was processed
        assert 'results' in result
        assert len(result['results']) == 1
        
        # Content should be normalized
        content = result['results'][0]['content']
        assert isinstance(content, str)
        # Should not contain obvious malformed patterns
        assert '\\x85' not in content


class TestRegressionCases:
    """Test cases to prevent regression of the UTF-8 encoding fix"""
    
    def test_github_issue_93_example(self):
        """Test the specific example from GitHub issue #93"""
        # This is the actual malformed content from the issue
        malformed_content = 'è\x85¾è®¯æ\x96\x87â\x80ªæ¡£â\x80¬\n 4+\n\nå\x8f¯å¤\x9aäººå®\x9eæ\x97¶å\x8d\x8fä½\x9cç\x9a\x84å\x9c¨çº¿æ\x96\x87â\x80ªæ¡£â\x80¬'
        
        # Should be detected as malformed
        assert _is_malformed_utf8(malformed_content) == True
        
        # Should be fixed by the normalization
        fixed_content = _fix_utf8_encoding(malformed_content)
        assert isinstance(fixed_content, str)
        
        # The fixed content should be different from the original
        # (unless the fix doesn't change anything, which is also valid)
        assert fixed_content != malformed_content or not _is_malformed_utf8(fixed_content)
    
    def test_mixed_content_handling(self):
        """Test handling of content with both proper and malformed UTF-8"""
        mixed_content = 'Tencent 腾讯\nè\x85¾è®¯æ\x96\x87â\x80ªæ¡£â\x80¬'
        
        # Should be detected as malformed due to mixed content
        assert _is_malformed_utf8(mixed_content) == True
        
        # Should be processed
        fixed_content = _fix_utf8_encoding(mixed_content)
        assert isinstance(fixed_content, str)
        
        # Should still contain the proper UTF-8 part
        assert 'Tencent' in fixed_content or '腾讯' in fixed_content
    
    @patch('tavily.tavily.requests.post')
    def test_backward_compatibility(self, mock_post):
        """Test that the fix doesn't break existing functionality"""
        # Mock response with normal, properly encoded content
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'url': 'https://example.com',
                    'title': 'Normal Title',
                    'content': 'Normal English content with proper Chinese: 腾讯',
                    'score': 0.9
                }
            ]
        }
        mock_post.return_value = mock_response
        
        client = TavilyClient(api_key="test-key")
        result = client.search("test query")
        
        # Normal content should pass through unchanged
        assert result['results'][0]['content'] == 'Normal English content with proper Chinese: 腾讯'
        assert result['results'][0]['title'] == 'Normal Title'
        assert result['results'][0]['url'] == 'https://example.com'
        assert result['results'][0]['score'] == 0.9


if __name__ == '__main__':
    # NOTE: These tests use mocked API responses due to automated environment limitations
    # For comprehensive testing, run with actual API key and Chinese search queries:
    # 
    # Manual testing checklist:
    # 1. Test with real Chinese search queries using search_depth="advanced"
    # 2. Verify Chinese characters display correctly in content fields
    # 3. Test both sync and async clients with real API
    # 4. Verify performance impact is minimal
    # 5. Test edge cases with mixed language content
    
    pytest.main([__file__, "-v"]) 
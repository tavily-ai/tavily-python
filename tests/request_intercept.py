from json import loads, dumps
import requests as vanilla_requests
import httpx
from contextlib import asynccontextmanager


vanilla_async_post = httpx.AsyncClient.post
vanilla_async_get = httpx.AsyncClient.get
try:
    vanilla_async_stream = httpx.AsyncClient.stream
except AttributeError:
    vanilla_async_stream = None

class Request:
    def __init__(self, method, url, headers=None, body=None, timeout=None, proxies=None):
        self.method = method
        self.url = url
        self.headers = headers
        self.timeout = timeout
        self.proxies = proxies
        self.body = body
    
    def json(self):
        return loads(self.body) if self.body else None

class Response:
    def __init__(self, status_code, headers=None, body=None):
        self.status_code = status_code
        self.headers = headers or {}
        self.body = body

    def json(self):
        return loads(self.body) if self.body else None
    
    def raise_for_status(self):
        pass
    
    def iter_content(self):
        """For sync streaming"""
        if self.body:
            body_bytes = self.body.encode('utf-8') if isinstance(self.body, str) else self.body
            yield body_bytes
        else:
            yield b''
    
    def close(self):
        pass

class MockSession:
    """Mock requests.Session for testing."""
    def __init__(self, interceptor):
        self._interceptor = interceptor
        self.headers = {}
        self.proxies = {}

    def post(self, url, data=None, headers=None, timeout=None, proxies=None, stream=False):
        # Merge session headers with request headers (request headers take precedence)
        merged_headers = {**self.headers, **(headers or {})}
        merged_proxies = {**self.proxies, **(proxies or {})} if proxies else self.proxies
        return self._interceptor.post(url, data, merged_headers, timeout, merged_proxies, stream)

    def get(self, url, headers=None, timeout=None, proxies=None):
        # Merge session headers with request headers (request headers take precedence)
        merged_headers = {**self.headers, **(headers or {})}
        merged_proxies = {**self.proxies, **(proxies or {})} if proxies else self.proxies
        return self._interceptor.get(url, merged_headers, timeout, merged_proxies)

    def close(self):
        pass


class Interceptor:
    def __init__(self):
        self._request = None
        self._response = Response(200, {"Content-Type": "application/json"}, '{"message": "OK"}')
        # Add exceptions attribute to match requests.exceptions
        class Exceptions:
            Timeout = TimeoutError
        self.exceptions = Exceptions()

    def Session(self):
        """Return a mock Session object."""
        return MockSession(self)

    def set_response(self, status_code, headers={}, body=None, json=None):
        if json is not None:
            body = dumps(json)
            headers["Content-Type"] = "application/json"

        self._response = Response(status_code, headers, body)

    def get_request(self):
        return self._request

    def post(self, url, data=None, headers=None, timeout=None, proxies=None, stream=False):
        self._request = Request("POST", url, headers, data, timeout, proxies)
        return self._response

    def get(self, url, headers=None, timeout=None, proxies=None):
        self._request = Request("GET", url, headers, None, timeout, proxies)
        return self._response

def intercept_requests(tavily):
    interceptor = Interceptor()
    if hasattr(tavily, 'requests'):
        tavily.requests = interceptor

    if hasattr(tavily, 'httpx'):
        async def post(self, url, content, timeout):
            return interceptor.post(
                url=str(self._base_url) + url,
                data=content,
                headers=self.headers,
                timeout=timeout
            )
        tavily.httpx.AsyncClient.post = post
        
        async def get(self, url, timeout=None):
            return interceptor.get(
                url=str(self._base_url) + url,
                headers=self.headers,
                timeout=timeout
            )
        tavily.httpx.AsyncClient.get = get
                
        class StreamResponse:
            def __init__(self, response):
                self.status_code = response.status_code
                self._response = response
            
            async def aread(self):
                body = self._response.body
                return body.encode('utf-8') if isinstance(body, str) else (body or b'')
            
            async def aiter_bytes(self):
                """Async iterator for response bytes"""
                if self._response.body:
                    body_bytes = self._response.body.encode('utf-8') if isinstance(self._response.body, str) else self._response.body
                    yield body_bytes
                else:
                    yield b''
            
            async def aclose(self):
                pass
        
        @asynccontextmanager
        async def stream(self, method, url, content=None, timeout=None):
            if method == "POST":
                interceptor._request = Request("POST", str(self._base_url) + url, self.headers, content, timeout, None)
            yield StreamResponse(interceptor._response)
        
        tavily.httpx.AsyncClient.stream = stream

    return interceptor

def clear_interceptor(tavily):
    if hasattr(tavily, 'requests'):
        tavily.requests = vanilla_requests

    if hasattr(tavily, 'httpx'):
        tavily.httpx.AsyncClient.post = vanilla_async_post
        tavily.httpx.AsyncClient.get = vanilla_async_get
        if hasattr(tavily.httpx.AsyncClient, 'stream') and vanilla_async_stream:
            tavily.httpx.AsyncClient.stream = vanilla_async_stream

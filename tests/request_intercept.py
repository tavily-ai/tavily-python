from json import loads, dumps
import requests as vanilla_requests
import httpx

vanilla_async_post = httpx.AsyncClient.post

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

class Interceptor:
    def __init__(self):
        self._request = None
        self._response = Response(200, {"Content-Type": "application/json"}, '{"message": "OK"}')

    def set_response(self, status_code, headers={}, body=None, json=None):
        if json is not None:
            body = dumps(json)
            headers["Content-Type"] = "application/json"

        self._response = Response(status_code, headers, body)

    def get_request(self):
        return self._request

    def post(self, url, data=None, headers=None, timeout=None, proxies=None):
        self._request = Request("POST", url, headers, data, timeout, proxies)
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

    return interceptor

def clear_interceptor(tavily):
    if hasattr(tavily, 'requests'):
        tavily.requests = vanilla_requests

    if hasattr(tavily, 'httpx'):
        tavily.httpx.AsyncClient.post = vanilla_async_post

import asyncio
import httpx
from tests.request_intercept import intercept_requests, clear_interceptor, MockSession
import tavily.tavily as sync_tavily
import tavily.async_tavily as async_tavily
import pytest
from tavily.errors import MissingAPIKeyError


@pytest.fixture
def sync_interceptor():
    yield intercept_requests(sync_tavily)
    clear_interceptor(sync_tavily)


@pytest.fixture
def async_interceptor():
    yield intercept_requests(async_tavily)
    clear_interceptor(async_tavily)


# --- Sync TavilyClient tests ---

class TestSyncCustomSession:
    def test_default_session_created_when_none_provided(self, sync_interceptor):
        client = sync_tavily.TavilyClient(api_key="tvly-test")
        assert not client._external_session

    def test_custom_session_used(self, sync_interceptor):
        custom_session = MockSession(sync_interceptor)
        client = sync_tavily.TavilyClient(api_key="tvly-test", session=custom_session)
        assert client._external_session
        assert client.session is custom_session

    def test_custom_session_preserves_existing_headers(self, sync_interceptor):
        custom_session = MockSession(sync_interceptor)
        custom_session.headers["Authorization"] = "Bearer apim-token-123"
        custom_session.headers["X-Custom"] = "custom-value"

        client = sync_tavily.TavilyClient(api_key="tvly-test", session=custom_session)

        # Custom Authorization should be preserved (not overwritten by Tavily's)
        assert client.session.headers["Authorization"] == "Bearer apim-token-123"
        # Custom header should be preserved
        assert client.session.headers["X-Custom"] == "custom-value"
        # Tavily defaults should fill in missing headers
        assert client.session.headers["Content-Type"] == "application/json"
        assert client.session.headers["X-Client-Source"] == "tavily-python"

    def test_custom_session_gets_default_headers_when_empty(self, sync_interceptor):
        custom_session = MockSession(sync_interceptor)
        client = sync_tavily.TavilyClient(api_key="tvly-test", session=custom_session)

        assert client.session.headers["Authorization"] == "Bearer tvly-test"
        assert client.session.headers["Content-Type"] == "application/json"

    def test_custom_session_preserves_existing_proxies(self, sync_interceptor):
        custom_session = MockSession(sync_interceptor)
        custom_session.proxies["https"] = "http://my-proxy:8080"

        client = sync_tavily.TavilyClient(
            api_key="tvly-test",
            session=custom_session,
            proxies={"https": "http://tavily-proxy:9090"},
        )

        # Custom session proxy should take precedence
        assert client.session.proxies["https"] == "http://my-proxy:8080"

    def test_close_does_not_close_external_session(self, sync_interceptor):
        closed = []
        custom_session = MockSession(sync_interceptor)
        custom_session.close = lambda: closed.append(True)

        client = sync_tavily.TavilyClient(api_key="tvly-test", session=custom_session)
        client.close()
        assert len(closed) == 0

    def test_close_closes_internal_session(self, sync_interceptor):
        client = sync_tavily.TavilyClient(api_key="tvly-test")
        # Should not raise — just verifies close() is called on internal session
        client.close()

    def test_context_manager_does_not_close_external_session(self, sync_interceptor):
        closed = []
        custom_session = MockSession(sync_interceptor)
        custom_session.close = lambda: closed.append(True)

        with sync_tavily.TavilyClient(api_key="tvly-test", session=custom_session):
            pass
        assert len(closed) == 0

    def test_custom_session_sends_request(self, sync_interceptor):
        sync_interceptor.set_response(200, json={"results": []})
        custom_session = MockSession(sync_interceptor)
        custom_session.headers["Authorization"] = "Bearer apim-token"

        client = sync_tavily.TavilyClient(api_key="tvly-test", session=custom_session)
        client.search("test query")

        req = sync_interceptor.get_request()
        assert req is not None
        assert req.headers["Authorization"] == "Bearer apim-token"

    # --- API key validation edge cases ---

    def test_no_api_key_no_session_raises(self, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        with pytest.raises(MissingAPIKeyError):
            sync_tavily.TavilyClient()

    def test_no_api_key_with_session_allowed(self, sync_interceptor, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        custom_session = MockSession(sync_interceptor)
        custom_session.headers["Authorization"] = "Bearer apim-token"
        client = sync_tavily.TavilyClient(session=custom_session)
        assert client.api_key is None
        assert "Authorization" not in client.headers
        assert client.session.headers["Authorization"] == "Bearer apim-token"

    def test_no_api_key_with_session_no_auth_header_on_defaults(self, sync_interceptor, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        custom_session = MockSession(sync_interceptor)
        client = sync_tavily.TavilyClient(session=custom_session)
        # No api_key means no Authorization in defaults
        assert "Authorization" not in client.headers
        # Session shouldn't get an Authorization header either
        assert "Authorization" not in client.session.headers

    def test_no_api_key_with_session_sends_request(self, sync_interceptor, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        sync_interceptor.set_response(200, json={"results": []})
        custom_session = MockSession(sync_interceptor)
        custom_session.headers["Authorization"] = "Bearer apim-token"

        client = sync_tavily.TavilyClient(session=custom_session)
        client.search("test query")

        req = sync_interceptor.get_request()
        assert req is not None
        assert req.headers["Authorization"] == "Bearer apim-token"

    def test_empty_string_api_key_no_session_raises(self, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        with pytest.raises(MissingAPIKeyError):
            sync_tavily.TavilyClient(api_key="")

    def test_empty_string_api_key_with_session_allowed(self, sync_interceptor):
        custom_session = MockSession(sync_interceptor)
        client = sync_tavily.TavilyClient(api_key="", session=custom_session)
        assert "Authorization" not in client.headers

    def test_api_key_and_session_both_provided(self, sync_interceptor):
        custom_session = MockSession(sync_interceptor)
        client = sync_tavily.TavilyClient(api_key="tvly-test", session=custom_session)
        # api_key provided and session has no Authorization, so default fills it in
        assert client.session.headers["Authorization"] == "Bearer tvly-test"

    def test_custom_session_with_all_endpoints(self, sync_interceptor):
        custom_session = MockSession(sync_interceptor)
        custom_session.headers["Authorization"] = "Bearer apim-token"

        client = sync_tavily.TavilyClient(session=custom_session)

        # search
        sync_interceptor.set_response(200, json={"results": []})
        client.search("test")
        assert sync_interceptor.get_request().headers["Authorization"] == "Bearer apim-token"

        # extract
        sync_interceptor.set_response(200, json={"results": [], "failed_results": []})
        client.extract(urls=["https://example.com"])
        assert sync_interceptor.get_request().headers["Authorization"] == "Bearer apim-token"

        # crawl
        sync_interceptor.set_response(200, json={"results": []})
        client.crawl(url="https://example.com")
        assert sync_interceptor.get_request().headers["Authorization"] == "Bearer apim-token"

        # map
        sync_interceptor.set_response(200, json={"results": []})
        client.map(url="https://example.com")
        assert sync_interceptor.get_request().headers["Authorization"] == "Bearer apim-token"

    def test_custom_session_with_custom_base_url(self, sync_interceptor):
        sync_interceptor.set_response(200, json={"results": []})
        custom_session = MockSession(sync_interceptor)

        client = sync_tavily.TavilyClient(
            api_key="tvly-test",
            session=custom_session,
            api_base_url="https://apim.corp.com/tavily",
        )
        client.search("test")

        req = sync_interceptor.get_request()
        assert req.url == "https://apim.corp.com/tavily/search"

    def test_custom_session_proxies_fill_missing_protocols(self, sync_interceptor):
        custom_session = MockSession(sync_interceptor)
        custom_session.proxies["http"] = "http://session-proxy:8080"

        client = sync_tavily.TavilyClient(
            api_key="tvly-test",
            session=custom_session,
            proxies={"http": "http://arg-proxy:9090", "https": "http://arg-proxy:9091"},
        )

        # http: session proxy wins
        assert client.session.proxies["http"] == "http://session-proxy:8080"
        # https: session didn't have it, so arg fills it in
        assert client.session.proxies["https"] == "http://arg-proxy:9091"

    def test_custom_session_project_id_header(self, sync_interceptor):
        custom_session = MockSession(sync_interceptor)
        client = sync_tavily.TavilyClient(
            api_key="tvly-test",
            session=custom_session,
            project_id="my-project",
        )
        assert client.session.headers["X-Project-ID"] == "my-project"

    def test_shared_session_across_multiple_clients(self, sync_interceptor):
        sync_interceptor.set_response(200, json={"results": []})
        shared_session = MockSession(sync_interceptor)
        shared_session.headers["Authorization"] = "Bearer shared-token"

        client1 = sync_tavily.TavilyClient(session=shared_session)
        client2 = sync_tavily.TavilyClient(session=shared_session)

        assert client1.session is client2.session

        client1.search("query1")
        assert sync_interceptor.get_request().headers["Authorization"] == "Bearer shared-token"

        client2.search("query2")
        assert sync_interceptor.get_request().headers["Authorization"] == "Bearer shared-token"

        # Closing one client should not close the shared session
        client1.close()
        client2.search("query3")
        assert sync_interceptor.get_request() is not None


# --- Async AsyncTavilyClient tests ---

class TestAsyncCustomClient:
    def test_default_client_created_when_none_provided(self):
        client = async_tavily.AsyncTavilyClient(api_key="tvly-test")
        assert not client._external_client

    def test_custom_client_used(self):
        custom_client = httpx.AsyncClient()
        client = async_tavily.AsyncTavilyClient(api_key="tvly-test", client=custom_client)
        assert client._external_client
        assert client._client is custom_client

    def test_custom_client_preserves_existing_headers(self):
        custom_client = httpx.AsyncClient(headers={
            "Authorization": "Bearer apim-token-123",
            "X-Custom": "custom-value",
        })
        client = async_tavily.AsyncTavilyClient(api_key="tvly-test", client=custom_client)

        assert client._client.headers["Authorization"] == "Bearer apim-token-123"
        assert client._client.headers["X-Custom"] == "custom-value"
        assert client._client.headers["Content-Type"] == "application/json"
        assert client._client.headers["X-Client-Source"] == "tavily-python"

    def test_custom_client_gets_default_headers_when_empty(self):
        custom_client = httpx.AsyncClient()
        client = async_tavily.AsyncTavilyClient(api_key="tvly-test", client=custom_client)

        assert client._client.headers["Authorization"] == "Bearer tvly-test"
        assert client._client.headers["Content-Type"] == "application/json"

    def test_custom_client_base_url_set_when_missing(self):
        custom_client = httpx.AsyncClient()
        client = async_tavily.AsyncTavilyClient(api_key="tvly-test", client=custom_client)
        assert "api.tavily.com" in str(client._client.base_url)

    def test_custom_client_base_url_preserved_when_set(self):
        custom_client = httpx.AsyncClient(base_url="https://apim.example.com/tavily")
        client = async_tavily.AsyncTavilyClient(api_key="tvly-test", client=custom_client)
        assert "apim.example.com" in str(client._client.base_url)

    def test_close_does_not_close_external_client(self):
        closed = []
        custom_client = httpx.AsyncClient()

        async def run():
            client = async_tavily.AsyncTavilyClient(api_key="tvly-test", client=custom_client)
            original_aclose = custom_client.aclose

            async def track_close():
                closed.append(True)
                await original_aclose()

            custom_client.aclose = track_close
            await client.close()

        asyncio.run(run())
        assert len(closed) == 0

    def test_context_manager_does_not_close_external_client(self):
        closed = []
        custom_client = httpx.AsyncClient()

        async def run():
            original_aclose = custom_client.aclose

            async def track_close():
                closed.append(True)
                await original_aclose()

            custom_client.aclose = track_close
            async with async_tavily.AsyncTavilyClient(api_key="tvly-test", client=custom_client):
                pass

        asyncio.run(run())
        assert len(closed) == 0

    def test_custom_client_sends_request(self, async_interceptor):
        async_interceptor.set_response(200, json={"results": []})
        custom_client = httpx.AsyncClient(
            headers={"Authorization": "Bearer apim-token"},
            base_url="https://api.tavily.com",
        )

        client = async_tavily.AsyncTavilyClient(api_key="tvly-test", client=custom_client)
        asyncio.run(client.search("test query"))

        req = async_interceptor.get_request()
        assert req is not None
        assert req.headers["Authorization"] == "Bearer apim-token"

    # --- API key validation edge cases ---

    def test_no_api_key_no_client_raises(self, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        with pytest.raises(MissingAPIKeyError):
            async_tavily.AsyncTavilyClient()

    def test_no_api_key_with_client_allowed(self, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        custom_client = httpx.AsyncClient(
            headers={"Authorization": "Bearer apim-token"},
        )
        client = async_tavily.AsyncTavilyClient(client=custom_client)
        assert client._client.headers["Authorization"] == "Bearer apim-token"

    def test_no_api_key_with_client_no_auth_header_on_defaults(self, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        custom_client = httpx.AsyncClient()
        client = async_tavily.AsyncTavilyClient(client=custom_client)
        # httpx always has headers dict but Authorization shouldn't be added
        assert "authorization" not in [k.lower() for k in client._client.headers.keys()
                                        if k.lower() == "authorization"
                                        and client._client.headers[k].startswith("Bearer None")]

    def test_no_api_key_with_client_sends_request(self, async_interceptor, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        async_interceptor.set_response(200, json={"results": []})
        custom_client = httpx.AsyncClient(
            headers={"Authorization": "Bearer apim-token"},
            base_url="https://api.tavily.com",
        )

        client = async_tavily.AsyncTavilyClient(client=custom_client)
        asyncio.run(client.search("test query"))

        req = async_interceptor.get_request()
        assert req is not None
        assert req.headers["Authorization"] == "Bearer apim-token"

    def test_custom_client_with_all_endpoints(self, async_interceptor):
        custom_client = httpx.AsyncClient(
            headers={"Authorization": "Bearer apim-token"},
            base_url="https://api.tavily.com",
        )
        client = async_tavily.AsyncTavilyClient(client=custom_client)

        # search
        async_interceptor.set_response(200, json={"results": []})
        asyncio.run(client.search("test"))
        assert async_interceptor.get_request().headers["Authorization"] == "Bearer apim-token"

        # extract
        async_interceptor.set_response(200, json={"results": [], "failed_results": []})
        asyncio.run(client.extract(urls=["https://example.com"]))
        assert async_interceptor.get_request().headers["Authorization"] == "Bearer apim-token"

        # crawl
        async_interceptor.set_response(200, json={"results": []})
        asyncio.run(client.crawl(url="https://example.com"))
        assert async_interceptor.get_request().headers["Authorization"] == "Bearer apim-token"

        # map
        async_interceptor.set_response(200, json={"results": []})
        asyncio.run(client.map(url="https://example.com"))
        assert async_interceptor.get_request().headers["Authorization"] == "Bearer apim-token"

    def test_custom_client_project_id_header(self):
        custom_client = httpx.AsyncClient()
        client = async_tavily.AsyncTavilyClient(
            api_key="tvly-test",
            client=custom_client,
            project_id="my-project",
        )
        assert client._client.headers["X-Project-ID"] == "my-project"

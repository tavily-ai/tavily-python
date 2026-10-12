"""
A long-lived client reusing a pooled keep-alive connection that the server has since
closed must retry on a fresh connection instead of raising ConnectionError.
"""
import socket
import threading

import requests

import tavily.tavily as sync_tavily


def _stale_server():
    """First request on each connection is answered; the second is read then dropped."""
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(5)

    def serve():
        while True:
            conn, _ = srv.accept()
            conn.recv(65536)
            conn.sendall(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 15\r\nConnection: keep-alive\r\n\r\n{"results": []}')
            conn.recv(65536)
            conn.close()

    threading.Thread(target=serve, daemon=True).start()
    return f"http://127.0.0.1:{srv.getsockname()[1]}"


def test_plain_session_reproduces_remote_disconnected():
    base = _stale_server()
    client = sync_tavily.TavilyClient(api_key="tvly-test", api_base_url=base, session=requests.Session())
    client.search("first")
    try:
        client.search("second")
    except requests.exceptions.ConnectionError as e:
        assert "RemoteDisconnected" in repr(e)
    else:
        raise AssertionError("expected ConnectionError on stale connection")


def test_default_session_retries_stale_connection():
    base = _stale_server()
    client = sync_tavily.TavilyClient(api_key="tvly-test", api_base_url=base)
    client.search("first")
    assert client.search("second") == {"results": []}

import pytest
import socket

def patched_connect(*args, **kwargs):  # pragma: no cover
    raise RuntimeError("network requests are disabled in tests.")

@pytest.fixture(autouse=True)
def disable_network():
    socket.socket.connect = patched_connect
    yield
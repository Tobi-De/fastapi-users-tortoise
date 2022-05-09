import asyncio
from typing import Any, Dict

import pytest


@pytest.fixture(scope="session")
def event_loop():
    """Force the pytest-asyncio loop to be the main one."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def oauth_account1() -> Dict[str, Any]:
    return {
        "oauth_name": "service1",
        "access_token": "TOKEN",
        "expires_at": 1579000751,
        "account_id": "user_oauth1",
        "account_email": "king.arthur@camelot.bt",
    }


@pytest.fixture
def oauth_account2() -> Dict[str, Any]:
    return {
        "oauth_name": "service2",
        "access_token": "TOKEN",
        "expires_at": 1579000751,
        "account_id": "user_oauth2",
        "account_email": "king.arthur@camelot.bt",
    }

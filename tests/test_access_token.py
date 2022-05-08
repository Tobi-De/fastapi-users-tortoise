from typing import AsyncGenerator, Any
from datetime import datetime, timezone, timedelta

import pytest

from fastapi_users_tortoise.access_token import TortoiseORMAccessTokenDatabase


@pytest.fixture
async def tortoise_access_token_db() -> AsyncGenerator[
    TortoiseORMAccessTokenDatabase, None
]:
    raise NotImplementedError()


@pytest.fixture
def user_id() -> Any:
    raise NotImplementedError()


class AccessToken:
    pass


@pytest.mark.asyncio
async def test_queries(
    tortoise_access_token_db: TortoiseORMAccessTokenDatabase[AccessToken],
    user_id: Any,
):
    access_token_create = {"token": "TOKEN", "user_id": user_id}

    # Create
    access_token = await tortoise_access_token_db.create(access_token_create)
    assert access_token.token == "TOKEN"
    assert access_token.user_id == user_id

    # Update
    update_dict = {"created_at": datetime.now(timezone.utc)}
    updated_access_token = await tortoise_access_token_db.update(
        access_token, update_dict
    )
    assert updated_access_token.created_at == update_dict["created_at"]

    # Get by token
    access_token_by_token = await tortoise_access_token_db.get_by_token(
        access_token.token
    )
    assert access_token_by_token is not None

    # Get by token expired
    access_token_by_token = await tortoise_access_token_db.get_by_token(
        access_token.token, max_age=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    assert access_token_by_token is None

    # Get by token not expired
    access_token_by_token = await tortoise_access_token_db.get_by_token(
        access_token.token, max_age=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    assert access_token_by_token is not None

    # Get by token unknown
    access_token_by_token = await tortoise_access_token_db.get_by_token(
        "NOT_EXISTING_TOKEN"
    )
    assert access_token_by_token is None

    # Delete token
    await tortoise_access_token_db.delete(access_token)
    deleted_access_token = await tortoise_access_token_db.get_by_token(
        access_token.token
    )
    assert deleted_access_token is None


@pytest.mark.asyncio
async def test_insert_existing_token(
    tortoise_access_token_db:TortoiseORMAccessTokenDatabase[AccessToken],
    user_id: Any,
):
    access_token_create = {"token": "TOKEN", "user_id": user_id}
    await tortoise_access_token_db.create(access_token_create)

    with pytest.raises(Exception):
        await tortoise_access_token_db.create(access_token_create)

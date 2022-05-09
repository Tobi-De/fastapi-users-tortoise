import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, AsyncGenerator

import pytest
from tortoise import Tortoise

from fastapi_users_tortoise import TortoiseBaseUserAccountModelUUID
from fastapi_users_tortoise.access_token import (
    TortoiseAccessTokenDatabase,
    TortoiseBaseAccessTokenModel,
)


class User(TortoiseBaseUserAccountModelUUID):
    pass


class AccessToken(TortoiseBaseAccessTokenModel):
    pass


@pytest.fixture
async def tortoise_access_token_db(
    user_id: uuid.UUID,
) -> AsyncGenerator[TortoiseAccessTokenDatabase, None]:
    DATABASE_URL = "sqlite://./test-tortoise-access-token.db"
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["tests.test_access_token"]},
    )
    await Tortoise.generate_schemas()

    user = User(
        id=user_id,
        email="lancelot@camelot.bt",
        hashed_password="guinevere",
        is_active=True,
        is_verified=True,
        is_superuser=False,
    )
    await user.save()

    yield TortoiseAccessTokenDatabase(AccessToken)

    await AccessToken.all().delete()
    await User.all().delete()
    await Tortoise.close_connections()


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.mark.asyncio
async def test_queries(
    tortoise_access_token_db: TortoiseAccessTokenDatabase[AccessToken],
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
    tortoise_access_token_db: TortoiseAccessTokenDatabase[AccessToken],
    user_id: Any,
):
    access_token_create = {"token": "TOKEN", "user_id": user_id}
    await tortoise_access_token_db.create(access_token_create)

    with pytest.raises(Exception):
        await tortoise_access_token_db.create(access_token_create)

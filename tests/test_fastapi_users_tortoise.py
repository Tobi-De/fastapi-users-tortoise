from typing import AsyncGenerator, Any, Dict

import pytest

from fastapi_users_tortoise import TortoiseORMUserDatabase


@pytest.fixture
async def tortoise_user_db() -> AsyncGenerator[TortoiseORMUserDatabase, None]:
    raise NotImplementedError()


@pytest.fixture
async def tortoise_user_db_oauth() -> AsyncGenerator[TortoiseORMUserDatabase, None]:
    raise NotImplementedError()


@pytest.mark.asyncio
async def test_queries(tortoise_user_db: TortoiseORMUserDatabase[User]):
    user_create = {
        "email": "lancelot@camelot.bt",
        "hashed_password": "guinevere",
    }

    # Create
    user = await tortoise_user_db.create(user_create)
    assert user.id is not None
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.email == user_create["email"]

    # Update
    updated_user = await tortoise_user_db.update(user, {"is_superuser": True})
    assert updated_user.is_superuser is True

    # Get by id
    id_user = await tortoise_user_db.get(user.id)
    assert id_user is not None
    assert id_user.id == user.id
    assert id_user.is_superuser is True

    # Get by email
    email_user = await tortoise_user_db.get_by_email(str(user_create["email"]))
    assert email_user is not None
    assert email_user.id == user.id

    # Get by uppercased email
    email_user = await tortoise_user_db.get_by_email("Lancelot@camelot.bt")
    assert email_user is not None
    assert email_user.id == user.id

    # Unknown user
    unknown_user = await tortoise_user_db.get_by_email("galahad@camelot.bt")
    assert unknown_user is None

    # Delete user
    await tortoise_user_db.delete(user)
    deleted_user = await tortoise_user_db.get(user.id)
    assert deleted_user is None

    # OAuth without defined table
    with pytest.raises(NotImplementedError):
        await tortoise_user_db.get_by_oauth_account("foo", "bar")
    with pytest.raises(NotImplementedError):
        await tortoise_user_db.add_oauth_account(user, {})
    with pytest.raises(NotImplementedError):
        oauth_account = OAuthAccount(**oauth_account1)
        await tortoise_user_db.update_oauth_account(user, oauth_account, {})


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "email,query,found",
    [
        ("lancelot@camelot.bt", "lancelot@camelot.bt", True),
        ("lancelot@camelot.bt", "LanceloT@camelot.bt", True),
        ("lancelot@camelot.bt", "lancelot.@camelot.bt", False),
        ("lancelot@camelot.bt", "lancelot.*", False),
        ("lancelot@camelot.bt", "lancelot+guinevere@camelot.bt", False),
        ("lancelot+guinevere@camelot.bt", "lancelot+guinevere@camelot.bt", True),
        ("lancelot+guinevere@camelot.bt", "lancelot.*", False),
        ("квіточка@пошта.укр", "квіточка@пошта.укр", True),
        ("квіточка@пошта.укр", "КВІТОЧКА@ПОШТА.УКР", True),
    ],
)
async def test_email_query(
    tortoise_user_db: TortoiseORMUserDatabase[User], email: str, query: str, found: bool
):
    user_create = {
        "email": email,
        "hashed_password": "guinevere",
    }
    user = await tortoise_user_db.create(user_create)

    email_user = await tortoise_user_db.get_by_email(query)

    if found:
        assert email_user is not None
        assert email_user.id == user.id
    else:
        assert email_user is None


@pytest.mark.asyncio
async def test_insert_existing_email(tortoise_user_db: TortoiseORMUserDatabase[User]):
    user_create = {
        "email": "lancelot@camelot.bt",
        "hashed_password": "guinevere",
    }
    await tortoise_user_db.create(user_create)

    with pytest.raises(Exception):
        await tortoise_user_db.create(user_create)


@pytest.mark.asyncio
async def test_queries_custom_fields(tortoise_user_db: TortoiseORMUserDatabase[User]):
    """It should output custom fields in query result."""
    user_create = {
        "email": "lancelot@camelot.bt",
        "hashed_password": "guinevere",
        "first_name": "Lancelot",
    }
    user = await tortoise_user_db.create(user_create)

    assert user.id is not None
    id_user = await tortoise_user_db.get(user.id)
    assert id_user is not None
    assert id_user.id == user.id
    assert id_user.first_name == user.first_name


@pytest.mark.asyncio
async def test_queries_oauth(
    tortoise_user_db_oauth: TortoiseORMUserDatabase[UserOAuth],
    oauth_account1: Dict[str, Any],
    oauth_account2: Dict[str, Any],
):
    user_create = {
        "email": "lancelot@camelot.bt",
        "hashed_password": "guinevere",
    }

    # Create
    user = await tortoise_user_db_oauth.create(user_create)
    assert user.id is not None

    # Add OAuth account
    user = await tortoise_user_db_oauth.add_oauth_account(user, oauth_account1)
    user = await tortoise_user_db_oauth.add_oauth_account(user, oauth_account2)
    assert len(user.oauth_accounts) == 2
    assert user.oauth_accounts[1].account_id == oauth_account2["account_id"]
    assert user.oauth_accounts[0].account_id == oauth_account1["account_id"]

    # Update
    user = await tortoise_user_db_oauth.update_oauth_account(
        user, user.oauth_accounts[0], {"access_token": "NEW_TOKEN"}
    )
    assert user.oauth_accounts[0].access_token == "NEW_TOKEN"

    # Get by id
    assert user.id is not None
    id_user = await tortoise_user_db_oauth.get(user.id)
    assert id_user is not None
    assert id_user.id == user.id
    assert id_user.oauth_accounts[0].access_token == "NEW_TOKEN"

    # Get by email
    email_user = await tortoise_user_db_oauth.get_by_email(user_create["email"])
    assert email_user is not None
    assert email_user.id == user.id
    assert len(email_user.oauth_accounts) == 2

    # Get by OAuth account
    oauth_user = await tortoise_user_db_oauth.get_by_oauth_account(
        oauth_account1["oauth_name"], oauth_account1["account_id"]
    )
    assert oauth_user is not None
    assert oauth_user.id == user.id

    # Unknown OAuth account
    unknown_oauth_user = await tortoise_user_db_oauth.get_by_oauth_account("foo", "bar")
    assert unknown_oauth_user is None

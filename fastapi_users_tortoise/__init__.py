"""FastAPI Users database adapter for Tortoise ORM."""
from typing import Any, Dict, Generic, Optional, Type, TypeVar, cast
from uuid import UUID

from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import ID, OAP
from tortoise import fields, models
from tortoise.exceptions import DoesNotExist

__version__ = "0.2.0"


class TortoiseBaseUserAccountModel(models.Model):
    """Base Tortoise ORM users model definition."""

    """For the moment I can't get this to work with tortoise :
      class User(TortoiseBaseUserAccountModel[uuid.UUID]):
          pass
      so using generics here to specify the id ID is pointless.
      """

    id: Any
    email: str = fields.CharField(index=True, unique=True, null=False, max_length=255)
    hashed_password: str = fields.CharField(null=False, max_length=1024)
    is_active = fields.BooleanField(default=True, null=False)
    is_superuser = fields.BooleanField(default=False, null=False)
    is_verified = fields.BooleanField(default=False, null=False)

    class Meta:
        abstract = True


UP_TORTOISE = TypeVar("UP_TORTOISE", bound=TortoiseBaseUserAccountModel)


class TortoiseBaseUserAccountModelUUID(TortoiseBaseUserAccountModel):
    id: UUID = fields.UUIDField(pk=True)

    class Meta:
        abstract = True


class TortoiseBaseUserOAuthAccountModel(models.Model):
    """Base Tortoise ORM OAuth account model definition."""

    id: Any
    oauth_name: str = fields.CharField(null=False, max_length=100)
    access_token: str = fields.CharField(null=False, max_length=1024)
    expires_at: int = fields.IntField(null=True)
    refresh_token: str = fields.CharField(null=True, max_length=1024)
    account_id: str = fields.CharField(index=True, null=False, max_length=255)
    account_email: str = fields.CharField(null=False, max_length=255)
    user = fields.ForeignKeyField("models.User", related_name="oauth_accounts")

    class Meta:
        abstract = True


class TortoiseBaseUserOAuthAccountModelUUID(TortoiseBaseUserOAuthAccountModel):
    id: UUID = fields.UUIDField(pk=True)

    class Meta:
        abstract = True


class TortoiseUserDatabase(Generic[UP_TORTOISE, ID], BaseUserDatabase[UP_TORTOISE, ID]):
    """
    Database adapter for Tortoise ORM.

    :param user_model: SQLAlchemy user model.
    :param oauth_account_model: Optional SQLAlchemy OAuth accounts model.
    """

    def __init__(
        self,
        user_model: Type[UP_TORTOISE],
        oauth_account_model: Optional[Type[TortoiseBaseUserOAuthAccountModel]] = None,
    ):
        self.user_model = user_model
        self.oauth_account_model = oauth_account_model

    async def get(self, id: ID) -> Optional[UP_TORTOISE]:
        """Get a single user by id."""
        try:
            query = self.user_model.get(id=id)
            if self.oauth_account_model is not None:
                query = query.prefetch_related("oauth_accounts")
            return await query
        except DoesNotExist:
            return None

    async def get_by_email(self, email: str) -> Optional[UP_TORTOISE]:
        """Get a single user by email."""
        query = self.user_model.filter(email__iexact=email).first()

        if self.oauth_account_model is not None:
            query = query.prefetch_related("oauth_accounts")

        return await query

    async def get_by_oauth_account(
        self, oauth: str, account_id: str
    ) -> Optional[UP_TORTOISE]:
        """Get a single user by OAuth account id."""
        if self.oauth_account_model is None:
            raise NotImplementedError()

        oauth_account = (
            await self.oauth_account_model.filter(
                account_id=account_id, oauth_name=oauth
            )
            .prefetch_related("user")
            .first()
        )
        if oauth_account is None:
            return None
        return cast(UP_TORTOISE, oauth_account.user)

    async def create(self, create_dict: Dict[str, Any]) -> UP_TORTOISE:
        """Create a user."""
        user = self.user_model(**create_dict)
        await user.save()
        await user.refresh_from_db()
        return user

    async def update(
        self, user: UP_TORTOISE, update_dict: Dict[str, Any]
    ) -> UP_TORTOISE:
        """Update a user."""
        for key, value in update_dict.items():
            setattr(user, key, value)
        await user.save(update_fields=update_dict.keys())
        await user.refresh_from_db()
        return cast(UP_TORTOISE, user)

    async def delete(self, user: UP_TORTOISE) -> None:
        """Delete a user."""
        await user.delete()

    async def add_oauth_account(
        self, user: UP_TORTOISE, create_dict: Dict[str, Any]
    ) -> UP_TORTOISE:
        """Create an OAuth account and add it to the user."""
        if self.oauth_account_model is None:
            raise NotImplementedError()

        oauth_account = self.oauth_account_model(**create_dict)
        oauth_account.user = user
        await oauth_account.save()
        await user.refresh_from_db()
        return user

    async def update_oauth_account(
        self,
        user: UP_TORTOISE,
        oauth_account: OAP,
        update_dict: Dict[str, Any],
    ) -> UP_TORTOISE:
        """Update an OAuth account on a user."""
        if self.oauth_account_model is None:
            raise NotImplementedError()

        for key, value in update_dict.items():
            setattr(oauth_account, key, value)
        await oauth_account.save(update_fields=update_dict.keys())  # type: ignore
        return user

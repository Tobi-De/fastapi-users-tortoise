"""FastAPI Users database adapter for Tortoise ORM."""
from typing import Any, Dict, Generic, Optional, Type

from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import ID, UP
from tortoise import fields, models
from tortoise.exceptions import DoesNotExist

__version__ = "0.1.0"


class TortoiseBaseUserAccountModel(Generic[ID], models.Model):
    """Base Tortoise ORM users model definition."""

    id: ID
    email = fields.CharField(index=True, unique=True, null=False, max_length=255)
    hashed_password = fields.CharField(null=False, max_length=1024)
    is_active = fields.BooleanField(default=True, null=False)
    is_superuser = fields.BooleanField(default=False, null=False)
    is_verified = fields.BooleanField(default=False, null=False)

    class Meta:
        abstract = True


class TortoiseBaseUserAccountModelUUID(TortoiseBaseUserAccountModel):
    id = fields.UUIDField(pk=True)

    class Meta:
        abstract = True


class TortoiseBaseUserOAuthAccountModel(Generic[ID], models.Model):
    """Base Tortoise ORM OAuth account model definition."""

    id: ID
    oauth_name = fields.CharField(null=False, max_length=100)
    access_token = fields.CharField(null=False, max_length=1024)
    expires_at = fields.IntField(null=True)
    refresh_token = fields.CharField(null=True, max_length=1024)
    account_id = fields.CharField(index=True, null=False, max_length=255)
    account_email = fields.CharField(null=False, max_length=255)
    user = fields.ForeignKeyField("models.User", related_name="oauth_accounts")

    class Meta:
        abstract = True


class TortoiseBaseUserOAuthAccountModelUUID(TortoiseBaseUserOAuthAccountModel):
    id = fields.UUIDField(pk=True)

    class Meta:
        abstract = True


class TortoiseUserDatabase(Generic[UP, ID], BaseUserDatabase[UP, ID]):
    """
    Database adapter for Tortoise ORM.

    :param user_model: SQLAlchemy user model.
    :param oauth_account_model: Optional SQLAlchemy OAuth accounts model.
    """

    def __init__(
        self,
        user_model: Type[TortoiseBaseUserAccountModel],
        oauth_account_model: Optional[Type[TortoiseBaseUserOAuthAccountModel]] = None,
    ):
        self.user_model = user_model
        self.oauth_account_model = oauth_account_model

    async def get(self, id: ID) -> Optional[TortoiseBaseUserAccountModel]:
        """Get a single user by id."""
        try:
            query = self.user_model.get(id=id)
            if self.oauth_account_model is not None:
                query = query.prefetch_related("oauth_accounts")
            return await query
        except DoesNotExist:
            return None

    async def get_by_email(self, email: str) -> Optional[TortoiseBaseUserAccountModel]:
        """Get a single user by email."""
        query = self.user_model.filter(email__iexact=email).first()

        if self.oauth_account_model is not None:
            query = query.prefetch_related("oauth_accounts")

        return await query

    async def get_by_oauth_account(
        self, oauth: str, account_id: str
    ) -> Optional[TortoiseBaseUserAccountModel]:
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
        return oauth_account.user

    async def create(self, create_dict: Dict[str, Any]) -> TortoiseBaseUserAccountModel:
        """Create a user."""
        user = self.user_model(**create_dict)
        await user.save()
        await user.refresh_from_db()
        return user

    async def update(
        self, user: TortoiseBaseUserAccountModel, update_dict: Dict[str, Any]
    ) -> TortoiseBaseUserAccountModel:
        """Update a user."""
        for key, value in update_dict.items():
            setattr(user, key, value)
        await user.save(update_fields=update_dict.keys())
        await user.refresh_from_db()
        return user

    async def delete(self, user: TortoiseBaseUserAccountModel) -> None:
        """Delete a user."""
        await user.delete()

    async def add_oauth_account(
        self, user: TortoiseBaseUserAccountModel, create_dict: Dict[str, Any]
    ) -> TortoiseBaseUserAccountModel:
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
        user: TortoiseBaseUserAccountModel,
        oauth_account: TortoiseBaseUserOAuthAccountModel,
        update_dict: Dict[str, Any],
    ) -> TortoiseBaseUserAccountModel:
        """Update an OAuth account on a user."""
        if self.oauth_account_model is None:
            raise NotImplementedError()

        for key, value in update_dict.items():
            setattr(oauth_account, key, value)
        await oauth_account.save(update_fields=update_dict.keys())
        return user

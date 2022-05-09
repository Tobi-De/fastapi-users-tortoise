"""FastAPI Users access token database adapter for Tortoise ORM."""
from datetime import datetime
from typing import Any, Dict, Generic, Optional, Type

from fastapi_users.authentication.strategy.db import AP, AccessTokenDatabase
from tortoise import fields, models


class TortoiseBaseAccessTokenModel(models.Model):
    """Tortoise access token model definition."""

    token = fields.CharField(pk=True, max_length=43, null=False)
    created_at: datetime = fields.DatetimeField(null=False, auto_now_add=True)
    user = fields.ForeignKeyField("models.User")

    class Meta:
        abstract = True


class TortoiseAccessTokenDatabase(Generic[AP], AccessTokenDatabase[AP]):
    """
    Access token database adapter for Tortoise ORM.
    :param access_token_model: Access token Tortoise ORM model.
    """

    def __init__(self, access_token_model: Type[AP]):
        self.access_token_model = access_token_model

    async def get_by_token(
        self, token: str, max_age: Optional[datetime] = None
    ) -> Optional[AP]:
        """Get a single access token by token."""
        query = self.access_token_model.filter(token=token)
        if max_age is not None:
            query = query.filter(created_at__gte=max_age)

        return await query.first()

    async def create(self, create_dict: Dict[str, Any]) -> AP:
        """Create an access token."""
        data = {**create_dict}
        user_id = data.pop("user_id")
        access_token = self.access_token_model(**data)
        access_token.user_id = user_id
        await access_token.save()
        await access_token.refresh_from_db()
        return access_token

    async def update(self, access_token: AP, update_dict: Dict[str, Any]) -> AP:
        """Update an access token."""
        for field, value in update_dict.items():
            setattr(access_token, field, value)
        await access_token.save()
        await access_token.refresh_from_db()
        return access_token

    async def delete(self, access_token: AP) -> None:
        """Delete an access token."""
        await self.access_token_model.filter(token=access_token.token).delete()

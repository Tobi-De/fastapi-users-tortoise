"""FastAPI Users access token database adapter for Tortoise ORM."""
from datetime import datetime
from typing import Any, Dict, Generic, Optional, Type, TypeVar, TYPE_CHECKING

from fastapi_users.authentication.strategy.db import AccessTokenDatabase
from tortoise import fields, models


class TortoiseBaseAccessTokenModel(models.Model):
    """Tortoise access token model definition."""

    """For the moment I can't get this to work with tortoise :
    class AccessToken(TortoiseBaseAccessTokenModel[uuid.UUID]):
        pass
    so using generics here to specify the id ID is pointless.
    """
    if TYPE_CHECKING:
        user_id: Any
    user = fields.ForeignKeyField("models.User")
    token: str = fields.CharField(pk=True, max_length=43, null=False)
    created_at: datetime = fields.DatetimeField(null=False, auto_now_add=True)

    class Meta:
        abstract = True


AP_TORTOISE = TypeVar("AP_TORTOISE", bound=TortoiseBaseAccessTokenModel)


class TortoiseAccessTokenDatabase(
    Generic[AP_TORTOISE], AccessTokenDatabase[AP_TORTOISE]
):
    """
    Access token database adapter for Tortoise ORM.
    :param access_token_model: Access token Tortoise ORM model.
    """

    def __init__(self, access_token_model: Type[AP_TORTOISE]):
        self.access_token_model = access_token_model

    async def get_by_token(
        self, token: str, max_age: Optional[datetime] = None
    ) -> Optional[AP_TORTOISE]:
        """Get a single access token by token."""
        query = self.access_token_model.filter(token=token)
        if max_age is not None:
            query = query.filter(created_at__gte=max_age)

        return await query.first()

    async def create(self, create_dict: Dict[str, Any]) -> AP_TORTOISE:
        """Create an access token."""
        data = {**create_dict}
        user_id = data.pop("user_id")
        access_token = self.access_token_model(**data)
        access_token.user_id = user_id
        await access_token.save()
        await access_token.refresh_from_db()
        return access_token

    async def update(
        self, access_token: AP_TORTOISE, update_dict: Dict[str, Any]
    ) -> AP_TORTOISE:
        """Update an access token."""
        for field, value in update_dict.items():
            setattr(access_token, field, value)
        await access_token.save()
        await access_token.refresh_from_db()
        return access_token

    async def delete(self, access_token: AP_TORTOISE) -> None:
        """Delete an access token."""
        await self.access_token_model.filter(token=access_token.token).delete()

FastAPI Users provides an optional OAuth2 authentication support.  Read the [official documentation on this](https://fastapi-users.github.io/fastapi-users/10.0/configuration/oauth/) for more details.

## Installation

In case you are confused on how to install dependencies:

```sh
pip install 'fastapi-users[oauth]'
```

## Configuration

### Instantiate an OAuth2 client

You first need to get an HTTPX OAuth client instance. [Read the documentation](https://frankie567.github.io/httpx-oauth/oauth2/) for more information.

```py
from httpx_oauth.clients.google import GoogleOAuth2

google_oauth_client = GoogleOAuth2("CLIENT_ID", "CLIENT_SECRET")
```

### Setup the database adapter

You'll need to define the Tortoise ORM model for storing OAuth accounts. We provide a base one for this:

```py
from fastapi_users_tortoise import TortoiseBaseUserOAuthAccountModelUUID, TortoiseBaseUserAccountModelUUID, TortoiseUserDatabase

class User(TortoiseBaseUserAccountModelUUID):
   pass

class OAuthAccount(TortoiseBaseUserOAuthAccountModelUUID):
    pass

async def get_user_db():
    yield TortoiseUserDatabase(User, OAuthAccount)
```

The base class `TortoiseBaseUserOAuthAccountModelUUID` already defines a foreign key to your user model like this:

You only need to change this if your user model is not called `User` or if it is not present in a [tortoise orm app/namespace](https://tortoise.github.io/setup.html) called `models`.

```python
from tortoise import fields, models

class TortoiseBaseUserOAuthAccountModel(models.Model):
    """Base Tortoise ORM OAuth account model definition."""
    ...
    user = fields.ForeignKeyField("models.User", related_name="oauth_accounts")
```
You only need to change this if your user model is not called `User` or if it is not present in a [tortoise orm app/namespace](https://tortoise.github.io/setup.html) called `models`.
However, you must keep the fields name as `user` and the related_name as `oauth_accounts`.

Besides, when instantiating the database adapter, we need pass this Tortoise ORM model as second argument.

!!! tip "Primary key is defined as UUID"
    By default, we use UUID as a primary key ID for your user. If you want to use another type, like an auto-incremented integer, you can use `TortoiseBaseUserOAuthAccountModel` as base class and define your own `id` field.

    ```py
    class OAuthAccount(TortoiseBaseUserOAuthAccountModel):
        id = fields.IntField(pk=True)

    ```


# Fastapi-users-tortoise

Tortoise orm database adapter for [fastapi-users v10](https://fastapi-users.github.io/fastapi-users/10.0/) and above.

## Installation

```sh
pip install fastapi-users-tortoise
```

## Usage

```python3
# models.py

from fastapi_users_tortoise import TortoiseBaseUserAccountModelUUID, TortoiseUserDatabase, TortoiseBaseUserOAuthAccountModelUUID
from fastapi_users_tortoise.access_token import TortoiseBaseAccessTokenModel, TortoiseAccessTokenDatabase
from tortoise import fields

class User(TortoiseBaseUserAccountModelUUID):
    full_name = fields.CharField(max_length=255, null=True)
    short_name = fields.CharField(max_length=255, null=True)

class OAuthAccount(TortoiseBaseUserOAuthAccountModelUUID):
    pass

async def get_user_db():
    yield TortoiseUserDatabase(User)


# If you need to store access token to the database

class AccessToken(TortoiseBaseAccessTokenModel):
    pass

async def get_access_token_db():
    yield TortoiseAccessTokenDatabase(AccessToken)

```

**Note**: Until the documentation is ready you can use the [fastapi-users sqlalchemy setup guide](https://fastapi-users.github.io/fastapi-users/10.0/configuration/databases/sqlalchemy/) as reference.


## Development

### Setup environment

You should create a virtual environment and activate it:

```bash
python -m venv venv/
```

```bash
source venv/bin/activate
```

And then install the development dependencies:

```bash
pip install -r requirements.dev.txt
```

### Run unit tests

You can run all the tests with:

```bash
make test
```

Alternatively, you can run `pytest` yourself:

```bash
pytest
```

There are quite a few unit tests, so you might run into ulimit issues where there are too many open file descriptors. You may be able to set a new, higher limit temporarily with:

```bash
ulimit -n 2048
```

### Format the code

Execute the following command to apply `isort` and `black` formatting:

```bash
make format
```

## TODO

- [ ] Improve type hint and generics usage

## License

This project is licensed under the terms of the MIT license.

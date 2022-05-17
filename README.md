# FastAPI Users - Database adapter for Tortoise ORM

Tortoise orm database adapter for [fastapi-users v10](https://fastapi-users.github.io/fastapi-users/10.0/) and above.
If you want an example of a project using this or just bootstrap your project with fastapi-users and tortoise, you can check out the cookiecutter I'm working on [here](https://github.com/Tobi-De/cookiecutter-fastapi).

[![pypi](https://badge.fury.io/py/fastapi-users-tortoise.svg)](https://pypi.org/project/fastapi-users-tortoise/)
[![python](https://img.shields.io/pypi/pyversions/fastapi-users-tortoise)](https://github.com/Tobi-De/fastapi-users-tortoise)
[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/Tobi-De/fastapi-users-tortoise/blob/master/LICENSE)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

**Documentation**: <a href="https://tobi-de.github.io/fastapi-users-tortoise/" target="_blank">https://tobi-de.github.io/fastapi-users-tortoise</a>

**Source Code**: <a href="https://github.com/tobi-de/fastapi-users-tortoise" target="_blank">https://github.com/tobi-de/fastapi-users-tortoise</a>

---

Add quickly a registration and authentication system to your [FastAPI](https://fastapi.tiangolo.com/) project. **FastAPI Users** is designed to be as customizable and adaptable as possible.

**Sub-package for Tortoise ORM support in FastAPI Users.**

## Installation

```sh
pip install fastapi-users-tortoise
```

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

## License

This project is licensed under the terms of the MIT license.

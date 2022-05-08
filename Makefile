install:
	python -m pip install --upgrade pip
	pip install flit
	flit install --deps develop

isort:
	isort ./fastapi_users_tortoise ./tests

format: isort
	black .

test:
	pytest --cov=fastapi_users_tortoise/ --cov-report=term-missing --cov-fail-under=100

bumpversion-major:
	bumpversion major

bumpversion-minor:
	bumpversion minor

bumpversion-patch:
	bumpversion patch

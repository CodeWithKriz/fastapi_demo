# fastapi_demo

## Virtual environment
* python3 -m venv venv
* source venv/bin/activate
* deactivate

## Run command
* uvicorn app.main:app --port 5000 --reload

## PIP Packages
* pip install "fastapi[all]"
* pip install "passlib[bcrypt]"
* pip install "python-jose[cryptography]"
* pip install alembic

## Alembic DB migration
* alembic init /<alembic-dir>
  - import the following modules
  - `from app.models import Base`
  - `from app.config import settings`
  - `config.set_main_option("sqlalchemy.url", settings.database_url)`
  - `target_metadata = Base.metadata`
* alembic revision --autogenerate -m "revision commit description"
* alembic upgrade head

## Docker Run command
* run container
  - `docker-compose -f docker-compose-dev.yml up --build`
* run container on daemon
  - `docker-compose -f docker-compose-dev.yml up -d`
* execute alembic upgrade
  - `docker-compose -f docker-compose-dev.yml exec api alembic upgrade head`

# APIs
![image](https://github.com/CodeWithKriz/fastapi_demo/assets/66562899/e6902441-f9e7-4955-a73c-6f0fc3a354b8)
![image](https://github.com/CodeWithKriz/fastapi_demo/assets/66562899/2ea7971f-7839-4107-b9af-523c475c7e86)

# Schemas
![image](https://github.com/CodeWithKriz/fastapi_demo/assets/66562899/562e6fa0-d575-41c3-8fd8-3114462500b5)

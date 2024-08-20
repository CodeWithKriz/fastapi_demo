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
* pip install pytest

## Alembic DB migration
* alembic init /<alembic-dir>
  - import the following modules
  - `from app.models import Base`
  - `from app.config import settings`
  - `config.set_main_option("sqlalchemy.url", settings.database_url)`
  - `target_metadata = Base.metadata`
* alembic revision --autogenerate -m "revision commit description"
* alembic upgrade head

## Environment Variables
* database_url
* test_db_url
* secret_key
* algorithm (`HS256` preferred)
* access_token_expire_minutes
* environment
* allowed_origins

# APIs & Schemas
![image](https://github.com/user-attachments/assets/f9e5471e-721e-4cf6-8df9-3f98e44aa4b1)
![image](https://github.com/user-attachments/assets/c238d89e-5bc7-4d70-a926-80f0eec06760)
![image](https://github.com/user-attachments/assets/7fdca465-06e8-4ffb-88ca-b662abbbd6f1)
![image](https://github.com/user-attachments/assets/72f942ae-6382-4063-96c4-2ab43755102a)

# fastapi_demo

### Virtual environment
* python3 -m venv venv
* source venv/bin/activate
* deactivate

### PIP Packages
* pip install "fastapi[all]"
* pip install "passlib[bcrypt]"
* pip install "python-jose[cryptography]"
* pip install alembic

### Alembic DB migration
* alembic init /<alembic-dir>
  - import the following modules
  - `from app.models import Base`
  - `from app.config import settings`
  - `config.set_main_option("sqlalchemy.url", settings.database_url)`
  - `target_metadata = Base.metadata`
* alembic revision --autogenerate -m "revision commit description"
* alembic upgrade head

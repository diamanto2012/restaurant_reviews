from __future__ import with_statement

from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User, Restaurant, Review

config = context.config

root_dir = os.path.dirname(os.path.dirname(__file__))
alembic_ini_path = os.path.join(root_dir, 'alembic.ini')

if os.path.exists(alembic_ini_path):
    fileConfig(alembic_ini_path)
else:
    try:
        fileConfig(config.config_file_name)
    except Exception as e:
        print(f"Предупреждение: Не удалось загрузить конфигурацию логирования: {e}")

app = create_app()
config.set_main_option('sqlalchemy.url', app.config['SQLALCHEMY_DATABASE_URI'])
target_metadata = db.metadata


def run_migrations_offline():
    """Запуск миграций в 'offline' режиме без подключения к БД."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Запуск миграций в 'online' режиме с подключением к БД."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

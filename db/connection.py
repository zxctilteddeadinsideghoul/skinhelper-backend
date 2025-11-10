from typing import Optional
from sqlalchemy import text
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.exc import ArgumentError, OperationalError
from sqlalchemy.orm import close_all_sessions, sessionmaker
from urllib.parse import quote_plus

from .config import config

_session_factory: Optional['sessionmaker'] = None
_db_engine: Optional['Engine'] = None


def _make_engine(url: str, echo: bool) -> 'Engine':
    """Создаёт SQLAlchemy Engine для PostgreSQL."""
    return create_engine(url, echo=echo, pool_pre_ping=True)


def _build_postgres_url() -> str:
    """Формирует URL подключения к PostgreSQL из параметров config."""
    user = getattr(config, "DB_USER", None)
    password = getattr(config, "DB_PASSWORD", None)
    host = getattr(config, "DB_HOST", "localhost")
    port = getattr(config, "DB_PORT", 5432)
    dbname = getattr(config, "DB_NAME", None)

    if not user or not dbname:
        print("\nERROR: Missing DB_USER or DB_NAME in config.\n")
        exit(1)

    password_enc = quote_plus(password) if password else ""
    return f"postgresql://{user}:{password_enc}@{host}:{port}/{dbname}"


def start_db_connections(engine_factory=_make_engine) -> None:
    """Инициализация подключения к БД."""
    global _db_engine, _session_factory

    if _db_engine:
        raise RuntimeError("DB connection is already initialized")

    db_url = _build_postgres_url()

    if not db_url.startswith("postgresql"):
        _db_url_error()

    try:
        _db_engine = engine_factory(db_url, echo=getattr(config, "ECHO", False))
        _session_factory = sessionmaker(
            autocommit=False, autoflush=False, expire_on_commit=False, bind=_db_engine
        )
        _check_conn()
    except (OperationalError, ArgumentError) as exc:
        _db_url_error(exc)


def stop_db_connections() -> None:
    """Закрывает все подключения и очищает фабрику сессий."""
    global _db_engine, _session_factory
    if not _db_engine:
        return

    close_all_sessions()
    _db_engine.dispose()
    _session_factory = None
    _db_engine = None


def get_engine() -> 'Engine':
    if not _db_engine:
        raise RuntimeError("DB connection was not initialized")
    return _db_engine


def get_session_factory():
    if _session_factory is None:
        raise RuntimeError("DB connection was not initialized")
    return _session_factory


def _db_url_error(exc=None):
    print(
        f'\n'
        f'Invalid PostgreSQL connection configuration:\n'
        f'URL or credentials seem to be incorrect.\n'
        f'Example: postgresql://user:password@localhost:5432/mydatabase\n'
        f'See https://docs.sqlalchemy.org/en/14/core/engines.html#postgresql for details.\n'
    )
    if exc:
        print(f'Error:\n{exc!s}\n')
    exit(1)


def _check_conn():
    """Проверяет соединение с базой."""
    s = _session_factory()
    try:
        s.execute(text('SELECT 1;'))
    finally:
        s.close()

from contextlib import contextmanager

from .connection import get_session_factory


@contextmanager
def session():
    _session = get_session_factory()()
    try:
        yield _session
    except:
        raise
    else:
        _session.commit()
    finally:
        _session.close()

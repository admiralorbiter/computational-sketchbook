from flask import g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

_engine = None
_Session = None

def init_db(app):
    db_url = app.config.get("DATABASE_URL", "sqlite:///var/bonzibuddy.db")
    global _engine, _Session
    os.makedirs("var", exist_ok=True)
    _engine = create_engine(db_url, future=True)
    _Session = sessionmaker(bind=_engine, future=True)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        sess = g.pop("db_session", None)
        if sess is not None:
            sess.close()

def get_session():
    if "db_session" not in g:
        g.db_session = _Session()
    return g.db_session

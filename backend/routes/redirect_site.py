from flask import g, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from ..utils.site import get_db_url, get_exists_site
from ..models.user import setup_db

db = SQLAlchemy()

database_connections = {}

def get_db_connection():
    host = request.headers.get("Host") 
    # retirar portas
    host = host.split(':')[0]
    if not get_exists_site(host):
        return None
    db_url = get_db_url(host)
    if not db_url:
        return None
    
    print(f"Conectando ao banco de dados de {host}")
    engine = create_engine(db_url)
    setup_db(engine)
    Session = scoped_session(sessionmaker(bind=engine))
    g.db_session = Session()
    return Session

def before_request():
    print('before_request')
    get_db_connection()


def disconnect_db(error=None):
    """Fecha a conexão do banco de dados no final da requisição"""
    db_engine = g.pop("db_engine", None)
    if db_engine is not None:
        db_engine.remove()

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base


SQLALCHEMY_DATABASE_URL = "sqlite:///./bookshop.db"
 
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
    )
 
SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)
 
Base = declarative_base()
 
def get_db():
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
 

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

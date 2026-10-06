from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dental_agents.models.state import Settings

Base = declarative_base()
engine = create_engine(url=Settings().DATABASE_URL)

LocalSession = sessionmaker(bind=engine)

def get_db_session():
    """
    Returns a new SQLAlchemy session for interacting with the database.
    """
    session = LocalSession()
    try:
        yield session
    finally:
        session.close()
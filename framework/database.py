import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import sessionmaker, declarative_base

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "dds_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "change_me")
DB_NAME = os.getenv("DB_NAME", "dds_platform")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_session():
    """Yield a database session, ensuring it is closed afterward.

    Use like:
        session = next(get_session())
    or, preferably, within a `with` block using SessionLocal() directly
    in route handlers.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

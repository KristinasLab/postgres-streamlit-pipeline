import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load .env only for local development
if os.getenv("RENDER") is None:
    load_dotenv()

# Prefer DATABASE_URL if available (Render)
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback for local Docker setup
if DATABASE_URL is None:
    DB_USER = quote_plus(os.getenv("DB_USER"))
    DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create a SessionLocal class for each database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 

# Base class for SQLAlchemy models
Base = declarative_base()

# Create tables (optional)
def init_db():
    # Create all tables that are defined in Base metadata
    Base.metadata.create_all(bind=engine)
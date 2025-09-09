import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve database credentials from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Create the database URL using the environment variables
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL) # This is the connection to the database

# Create a SessionLocal class for each database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 

# Base class for SQLAlchemy models
Base = declarative_base()

# Create tables (optional)
def init_db():
    # Create all tables that are defined in Base metadata
    Base.metadata.create_all(bind=engine)
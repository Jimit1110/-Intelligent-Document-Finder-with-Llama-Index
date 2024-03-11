"""This code sets up a SQLAlchemy engine to connect to a PostgreSQL database and creates a sessionmaker for managing database sessions."""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:admin123@localhost/user_data'

#create a SQLAlchemy engine to connect to the PostgreSQL database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

#create a sessionmaker bound to the engine for managing database sessions
SessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)
#declarative base is also created to serve as a base class for declarative ORM classes.
Base=declarative_base()
from sqlalchemy import String, Integer, Column
from database_con import Base

#this class defines the structure of the 'users' table in the database
#it inherits from the Base class provided by SQLAlchemy and defines three columns
class Users(Base):
    __tablename__ = "users"
    id= Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hash_password = Column(String, index=True)
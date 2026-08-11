from sqlalchemy import Column,String ,Integer, ForeignKey ,Boolean
from sqlalchemy.orm import relationship
from database import Base 

class User(Base):
    __tablename__ = "users"

    id = Column(Integer , primary_key=True)
    email = Column(String , unique=True , index=True , nullable=False)
    hashed_password  = Column(String , nullable=False)

    tasks = relationship("Task" , back_populates="owner", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer , primary_key=True , index=True)
    title = Column(String ,nullable=False)
    description = Column(String , nullable=True)
    completed = Column(Boolean , default=False)
    owner_id = Column(Integer , ForeignKey("users.id"), nullable=False)

    owner = relationship("User" , back_populates="tasks")
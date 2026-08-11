from pydantic import BaseModel , EmailStr 
from typing import Optional


#------------------user schema----------------

class UserCreate(BaseModel):
    email:  EmailStr 
    password:  str

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class config:
        from_attributes = True

#-----------------task schema------------------

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: int
    completed: bool
    owner_id: int

    class config:
        from_attributes = True

#-----------------auth schema-----------------

class Token(BaseModel):
    access_token: str
    token_type: str ="bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
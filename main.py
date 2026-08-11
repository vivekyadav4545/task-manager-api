from fastapi import FastAPI
import os
from slowapi import Limiter , _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


from database import engine , Base 
from models import User , Task
import users ,tasks
from limiter import limiter

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)



app.include_router(users.router)
app.include_router(tasks.router)



import pytest
import os 
os.environ["TESTING"] = "true"

## this is added because of redis
import asyncio
import sys


from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# this is used to solve problem of event loop closed
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()

from main import app
from database import Base, get_db

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:random@localhost:5432/taskmanager_test"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function" , autouse=True)
def create_and_delete_db():
    Base.metadata.create_all(bind= engine)
    yield
    Base.metadata.drop_all(bind= engine)

##to  solve the problem of redis event loop closed
@pytest.fixture(scope="function", autouse=True)
def reset_redis_client():
    yield
    import cache
    import redis.asyncio as redis
    from config import settings
    cache.redis_client = redis.from_url(settings.redis_url, decode_responses=True)


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c

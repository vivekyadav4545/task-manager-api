import pytest
import os 
os.environ["TESTING"] = "true"

from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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

@pytest.fixture()
def client():
    return TestClient(app)

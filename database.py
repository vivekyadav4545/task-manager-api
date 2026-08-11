from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker 
from config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autoflush=False, autocommit=False , bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

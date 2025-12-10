from sqlalchemy import create_engine
from app.database.base import Base
from app.core.config import settings

def init_db():
    """Initialize the database"""
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
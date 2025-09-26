from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Thay username, password, host, port, dbname bằng của bạn
DATABASE_URL = "postgresql+psycopg2://postgres:root@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency để tạo session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Thay username, password, host, port, dbname bằng của bạn
DATABASE_URL = "postgresql://neondb_owner:npg_dG15EQBmfDyj@ep-tiny-waterfall-a1g5po5b-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

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

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models, schemas
from sqlalchemy import text
from passlib.hash import bcrypt
from datetime import timedelta
from auth import create_access_token

app = FastAPI()

# Tạo bảng khi khởi động + check DB
@app.on_event("startup")
def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connected & tables created")
    except Exception as e:
        print("❌ Database connection failed:", e)


# ---------------- REGISTER ----------------
@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check username/email tồn tại chưa
    db_user = db.query(models.User).filter(
        (models.User.username == user.username) |
        (models.User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or Email already registered")

    # Hash password
    hashed_pw = bcrypt.hash(user.password)

    new_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        password=hashed_pw,
        email=user.email,
        role=user.role,
        avatar=user.avatar
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ---------------- LOGIN ----------------
@app.post("/login", response_model=schemas.TokenResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    # tìm user theo username
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user or not bcrypt.verify(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # tạo access token
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"msg": "FastAPI with PostgreSQL & JWT is running 🚀"}

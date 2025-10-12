from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from database import engine, Base, get_db
from passlib.hash import bcrypt
from auth import create_access_token, get_current_user
from typing import Optional, List
import entity, model, base64

# ==========================================================
# 🚀 Khởi tạo ứng dụng
# ==========================================================
app = FastAPI(
    title="🏋️ Fitness API",
    description="API quản lý sản phẩm và lịch tập có xác thực người dùng (OAuth2 Password Flow)",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True}
)

# ==========================================================
# 🌐 Cấu hình CORS
# ==========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hoặc ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# ⚙️ Kiểm tra DB khi khởi động
# ==========================================================
@app.on_event("startup")
def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database connected & tables created")
    except Exception as e:
        print("❌ Database connection failed:", e)

# ==========================================================
# 👤 REGISTER
# ==========================================================
@app.post("/register", response_model=model.UserResponse)
def register(user: model.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(entity.User).filter(
        (entity.User.username == user.username) |
        (entity.User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or Email already registered")

    hashed_pw = bcrypt.hash(user.password)
    new_user = entity.User(
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

# ==========================================================
# 🔐 LOGIN (chuẩn OAuth2 Password Flow)
# ==========================================================
@app.post("/login", response_model=model.TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(entity.User).filter(entity.User.username == form_data.username).first()
    if not user or not bcrypt.verify(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ==========================================================
# 🙋‍♂️ LẤY THÔNG TIN USER HIỆN TẠI
# ==========================================================
@app.get("/me", response_model=model.UserResponse)
def get_my_profile(current_user: entity.User = Depends(get_current_user)):
    return current_user

# ==========================================================
# 🟢 CREATE PRODUCT
# ==========================================================
@app.post("/products")
async def create_product(
    product_name: str = Form(...),
    product_desc: str = Form(None),
    product_type: str = Form(None),
    product_price: float = Form(...),
    product_image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: entity.User = Depends(get_current_user)
):
    image_bytes = await product_image.read() if product_image else None

    new_product = entity.Product(
        product_name=product_name,
        product_desc=product_desc,
        product_type=product_type,
        product_price=product_price,
        product_image=image_bytes
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"msg": "✅ Product created", "product_id": new_product.id}

# ==========================================================
# 🔵 GET ALL PRODUCTS
# ==========================================================
@app.get("/products")
def get_products(
    db: Session = Depends(get_db),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    product_type: Optional[str] = Query(None),
    current_user: entity.User = Depends(get_current_user)
):
    query = db.query(entity.Product).filter(entity.Product.deleted == False)

    if min_price is not None:
        query = query.filter(entity.Product.product_price >= min_price)
    if max_price is not None:
        query = query.filter(entity.Product.product_price <= max_price)
    if product_type:
        query = query.filter(entity.Product.product_type == product_type)

    products = query.all()
    result = []
    for p in products:
        result.append({
            "id": p.id,
            "product_name": p.product_name,
            "product_desc": p.product_desc,
            "product_type": p.product_type,
            "product_price": p.product_price,
            "deleted": p.deleted,
            "product_image": base64.b64encode(p.product_image).decode('utf-8') if p.product_image else None
        })
    return result

# ==========================================================
# 🟠 UPDATE PRODUCT
# ==========================================================
@app.put("/products/{product_id}")
async def update_product(
    product_id: int,
    product_name: str = Form(None),
    product_desc: str = Form(None),
    product_type: str = Form(None),
    product_price: float = Form(None),
    product_image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: entity.User = Depends(get_current_user)
):
    product = db.query(entity.Product).filter(entity.Product.id == product_id).first()
    if not product or product.deleted:
        raise HTTPException(status_code=404, detail="Product not found")

    if product_name:
        product.product_name = product_name
    if product_desc:
        product.product_desc = product_desc
    if product_type:
        product.product_type = product_type
    if product_price is not None:
        product.product_price = product_price
    if product_image:
        product.product_image = await product_image.read()

    db.commit()
    db.refresh(product)
    return {"msg": "✅ Product updated", "product_id": product.id}

# ==========================================================
# 🔴 SOFT DELETE PRODUCT
# ==========================================================
@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: entity.User = Depends(get_current_user)
):
    product = db.query(entity.Product).filter(entity.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.deleted = True
    db.commit()
    return {"msg": f"🗑️ Product {product_id} soft deleted"}

# ==========================================================
# 🏋️ CRUD CHO SCHEDULE (gắn với user)
# ==========================================================

@app.post("/schedules", response_model=model.ScheduleResponse)
def create_schedule(
    schedule: model.ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: entity.User = Depends(get_current_user)
):
    new_schedule = entity.Schedule(
        day_of_week=schedule.day_of_week,
        exercise_name=schedule.exercise_name,
        sets=schedule.sets,
        reps=schedule.reps,
        weight=schedule.weight,
        user_id=current_user.id   # ✅ lấy user từ token
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule


@app.get("/schedules", response_model=List[model.ScheduleResponse])
def get_schedules(
    db: Session = Depends(get_db),
    current_user: entity.User = Depends(get_current_user)
):
    # ✅ chỉ lấy schedule của user hiện tại
    schedules = db.query(entity.Schedule).filter(
        entity.Schedule.deleted == False,
        entity.Schedule.user_id == current_user.id
    ).all()
    return schedules


@app.put("/schedules/{schedule_id}", response_model=model.ScheduleResponse)
def update_schedule(
    schedule_id: int,
    updated: model.ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: entity.User = Depends(get_current_user)
):
    schedule = db.query(entity.Schedule).filter(
        entity.Schedule.id == schedule_id,
        entity.Schedule.user_id == current_user.id,  # ✅ chỉ được sửa schedule của mình
        entity.Schedule.deleted == False
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found or access denied")

    schedule.day_of_week = updated.day_of_week
    schedule.exercise_name = updated.exercise_name
    schedule.sets = updated.sets
    schedule.reps = updated.reps
    schedule.weight = updated.weight

    db.commit()
    db.refresh(schedule)
    return schedule


@app.delete("/schedules/{schedule_id}")
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: entity.User = Depends(get_current_user)
):
    schedule = db.query(entity.Schedule).filter(
        entity.Schedule.id == schedule_id,
        entity.Schedule.user_id == current_user.id  # ✅ chỉ được xóa của mình
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found or access denied")

    schedule.deleted = True
    db.commit()
    return {"msg": f"🗑️ Schedule {schedule_id} soft deleted"}

# ==========================================================
# 🚀 Run local
# ==========================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

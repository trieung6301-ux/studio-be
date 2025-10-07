from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import entity, model
from sqlalchemy import text
from passlib.hash import bcrypt
from datetime import timedelta
from auth import create_access_token
import base64

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
@app.post("/register", response_model=model.UserResponse)
def register(user: model.UserCreate, db: Session = Depends(get_db)):
    # Check username/email tồn tại chưa
    db_user = db.query(entity.User).filter(
        (entity.User.username == user.username) |
        (entity.User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or Email already registered")

    # Hash password
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


# ---------------- LOGIN ----------------
@app.post("/login", response_model=model.TokenResponse)
def login(request: model.LoginRequest, db: Session = Depends(get_db)):
    # tìm user theo username
    user = db.query(entity.User).filter(entity.User.username == request.username).first()
    if not user or not bcrypt.verify(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # tạo access token
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 🟢 CREATE Product
@app.post("/products")
async def create_product(
    product_name: str = Form(...),
    product_desc: str = Form(None),
    product_type: str = Form(None),
    product_price: float = Form(...),
    product_image: UploadFile = File(None),
    db: Session = Depends(get_db)
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



# 🔵 READ All Products (chỉ lấy chưa bị xóa)
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(entity.Product).filter(entity.Product.deleted == False).all()
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


# 🟡 READ Product by ID
@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(entity.Product).filter(entity.Product.id == product_id, entity.Product.deleted == False).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "id": product.id,
        "product_name": product.product_name,
        "product_desc": product.product_desc,
        "product_type": product.product_type,
        "product_price": product.product_price,
        "deleted": product.deleted,
        "product_image": base64.b64encode(product.product_image).decode('utf-8') if product.product_image else None
    }


# 🟠 UPDATE Product
@app.put("/products/{product_id}")
async def update_product(
    product_id: int,
    product_name: str = Form(None),
    product_desc: str = Form(None),
    product_type: str = Form(None),
    product_price: float = Form(None),
    product_image: UploadFile = File(None),
    db: Session = Depends(get_db)
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


# 🔴 SOFT DELETE Product
@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(entity.Product).filter(entity.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.deleted = True
    db.commit()
    return {"msg": f"🗑️ Product {product_id} soft deleted"}


# This is important for Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router
from database import Base, engine

app = FastAPI(
    title="🏋️ Fitness API",
    description="API quản lý sản phẩm và lịch tập có xác thực người dùng (OAuth2 Password Flow)",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

app.include_router(router)


# ==========================================================
# 🌐 Cấu hình CORS
# ==========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
# 🚀 Run local
# ==========================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

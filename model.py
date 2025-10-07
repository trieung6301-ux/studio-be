from pydantic import BaseModel

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    email: str
    role: str
    avatar: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: str
    role: str
    avatar: str

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ProductResponse(BaseModel):
    id: int
    product_name: str
    product_desc: str
    product_type: str
    product_price: float
    deleted: bool

    class Config:
        from_attributes = True

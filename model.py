from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    email: str
    role: Optional[str] = None
    avatar: Optional[str] = None

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










class ScheduleBase(BaseModel):
    day_of_week: str
    exercise_name: str
    sets: int
    reps: int
    weight: float | None = None

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleResponse(ScheduleBase):
    id: int
    deleted: bool
    user_id: int

    class Config:
        from_attributes = True



class OrderBase(BaseModel):
    name: str
    address: str
    phone_number: str
    email: str

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from typing import Optional


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


class ForgotPassword(BaseModel):
    email: str


class VerifyEmail(BaseModel):
    email: EmailStr
    otp: str


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: Optional[str] = None
    google_firebase_uid: Optional[str] = None

    phone: Optional[str] = None
    address: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None


class UserUpdate(BaseModel):
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    firebase_token: Optional[str] = None


class UserResponse(UserBase):
    id: int
    phone: Optional[str] = None
    address: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    google_firebase_uid: Optional[str] = None
    email_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

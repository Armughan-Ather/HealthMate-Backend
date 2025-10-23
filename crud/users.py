from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models.users import User
from schemas.users import UserCreate, UserUpdate
from utilities.email import send_email
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
import jwt
import re
import random
from fastapi import HTTPException, status
from pydantic import EmailStr,validate_email, ValidationError
from email_validator import validate_email, EmailNotValidError
load_dotenv()
FRONTEND_URL = os.getenv("FRONTEND_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_otp() -> str:
    """Generate a 6-digit OTP."""
    return f"{random.randint(10000, 99999)}"

def send_emailverification_email(recipient_email: str, otp: str):
    subject = "HealthMate – Verify Your Email Address"
    body = f"""
    Hello,

    Thank you for signing up with HealthMate!

    Your email verification code is: **{otp}**

    This code will expire in 10 minutes.

    If you did not sign up for a HealthMate account, you can safely ignore this email.

    Best regards,  
    Support Team
    """
    try:
        send_email(recipient_email, subject, body)
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def send_forgotpassword_email(recipient_email: str, otp: str):
    subject = "HealthMate – Password Reset Code"
    body = f"""
    Hello,

    We received a request to reset your HealthMate account password.

    Your OTP code is: **{otp}**

    This code will expire in 10 minutes.

    If you didn’t request this, you can safely ignore this email.

    Best regards,  
    Support Team
    """
    try:
        send_email(recipient_email, subject, body)
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"user_id": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        return None
    return user


def create_user(db: Session, user_data: UserCreate):
    # Validate raw password
    if user_data.password:
        password = user_data.password
        if len(user_data.password) > 72:
            raise HTTPException(status_code=400, detail="Password must not exceed 72 characters.")
        if len(password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise HTTPException(status_code=400, detail="Password must contain at least one number")
        if len(password) > 72:
            raise HTTPException(status_code=400, detail="Password must not exceed 72 characters.")

        hashed_password = hash_password(password)
    hashed_password = hash_password(user_data.password) if user_data.password else None
    user = User(
        email=user_data.email,
        name=user_data.name,
        password=hashed_password,
        phone=user_data.phone,
        address=user_data.address,
        gender=user_data.gender,
        date_of_birth=user_data.date_of_birth
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_firebase_user(
    db: Session, firebase_uid: str, email: str, provider: str, name: str
):
    user = db.query(User).filter(User.email == email).first()

    if user:
        # Update the corresponding Firebase UID field if it's not already set
        if provider == "google.com" and not user.google_firebase_uid:
            user.google_firebase_uid = firebase_uid
        
        db.commit()
        db.refresh(user)
        return user

    # No user with this email exists, create a new one
    user = User(
        email=email,
        name=name,
        google_firebase_uid=firebase_uid if provider == "google" else None,
        
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, user_data: UserUpdate):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    # Update fields if present
    if user_data.name is not None:
        user.name = user_data.name

    if user_data.phone is not None:
        user.phone = user_data.phone
    if user_data.address is not None:
        user.address = user_data.address
    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    if user_data.bp_systolic_min is not None:
        user.bp_systolic_min = user_data.bp_systolic_min
    if user_data.bp_systolic_max is not None:
        user.bp_systolic_max = user_data.bp_systolic_max
    if user_data.bp_diastolic_min is not None:
        user.bp_diastolic_min = user_data.bp_diastolic_min
    if user_data.bp_diastolic_max is not None:
        user.bp_diastolic_max = user_data.bp_diastolic_max

    if user_data.sugar_fasting_min is not None:
        user.sugar_fasting_min = user_data.sugar_fasting_min
    if user_data.sugar_fasting_max is not None:
        user.sugar_fasting_max = user_data.sugar_fasting_max
    if user_data.sugar_random_min is not None:
        user.sugar_random_min = user_data.sugar_random_min
    if user_data.sugar_random_max is not None:
        user.sugar_random_max = user_data.sugar_random_max

    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user


# def add_attendant_email(db: Session, user_id: int, email: str):
#     raise HTTPException(status_code=410, detail="Attendant emails deprecated; use connections API")


# def delete_attendant_email(db: Session, user_id: int, email: str):
#     raise HTTPException(status_code=410, detail="Attendant emails deprecated; use connections API")


# def update_single_attendant_email(db: Session, user_id: int, old_email: str, new_email: str):
#     raise HTTPException(status_code=410, detail="Attendant emails deprecated; use connections API")

# def send_email_to_attendants(attendant_emails: list[str], subject: str, body: str):
#     if not attendant_emails:
#         print("⚠️ No attendant emails provided.")
#         return {"sent_to": [], "failed": []}

#     sent_emails = []
#     failed_emails = []

#     for email in attendant_emails:
#         try:
#             send_email(email, subject, body)
#             sent_emails.append(email)
#         except Exception as e:
#             print(f"❌ Failed to send email to {email}: {e}")
#             failed_emails.append({"email": email, "error": str(e)})

#     return {"sent_to": sent_emails, "failed": failed_emails}
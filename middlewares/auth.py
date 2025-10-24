from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from database import get_db
from sqlalchemy.orm import Session
from models.users import User
from firebase_admin import auth as firebase_auth
from constants.enums import UserRoleEnum

from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_scheme = APIKeyHeader(name="Authorization")

def get_current_user_without_role(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except (ExpiredSignatureError, InvalidTokenError):
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        role: UserRoleEnum = payload.get("role") or None
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No active role selected. Please switch role first."
            )
        role_str = payload.get("role")
        role = UserRoleEnum(role_str) if role_str else None
        setattr(user, "active_role", role)
        return user
    except (ExpiredSignatureError, InvalidTokenError):
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

def require_role(*allowed_roles: UserRoleEnum):
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.active_role not in allowed_roles:
            allowed_names = ', '.join(r.value for r in allowed_roles)
            raise HTTPException(
                status_code=403,
                detail=f"Access restricted to roles: {allowed_names}"
            )
        return current_user
    return dependency


# Role-specific shortcuts
require_patient = require_role(UserRoleEnum.PATIENT)
require_doctor = require_role(UserRoleEnum.DOCTOR)
require_attendant = require_role(UserRoleEnum.ATTENDANT)
require_medical_staff = require_role(UserRoleEnum.DOCTOR, UserRoleEnum.ATTENDANT)


def verify_firebase_token(token: str):
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except firebase_auth.InvalidIdTokenError:
        print("Firebase token verification failed: Invalid token")
        return None
    except firebase_auth.ExpiredIdTokenError:
        print("Firebase token verification failed: Token expired")
        return None
    except firebase_auth.RevokedIdTokenError:
        print("Firebase token verification failed: Token revoked")
        return None
    except Exception as e:
        print(f"Firebase token verification failed: {str(e)}")
        return None

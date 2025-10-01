import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class UserRoleEnum(enum.Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ATTENDANT = "ATTENDANT"


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum(UserRoleEnum), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="roles")

    __table_args__ = (
        UniqueConstraint('user_id', 'role', name='unique_user_role'),
    )



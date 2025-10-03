from sqlalchemy import (
    Column, Integer, 
    DateTime, ForeignKey, Enum, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from database import Base
from constants.enums import RoleEnum


class UserRole(Base):
    __tablename__ = 'user_roles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role = Column(Enum(RoleEnum), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="roles")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'role', name='uq_user_role'),
        Index('idx_user_role_lookup', 'user_id', 'role'),
    )

    @validates('user_id')
    def validate_user_id(self, key, value):
        if value is None:
            raise ValueError("user_id is required")
        if value <= 0:
            raise ValueError("user_id must be a positive integer")
        return value

    @validates('role')
    def validate_role(self, key, value):
        if value is None:
            raise ValueError("role is required")
        if not isinstance(value, RoleEnum):
            raise ValueError("Invalid role value")
        return value
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base


class ConnectionTypeEnum(enum.Enum):
    DOCTOR = "DOCTOR"
    ATTENDANT = "ATTENDANT"


class ConnectionStatusEnum(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    REVOKED = "REVOKED"


class Connection(Base):
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    connected_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    connection_type = Column(Enum(ConnectionTypeEnum), nullable=False)
    status = Column(Enum(ConnectionStatusEnum), nullable=False)
    request_message = Column(Text, nullable=True)
    requested_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint('patient_id', 'connected_user_id', 'connection_type', name='unique_connection'),
        CheckConstraint('patient_id != connected_user_id', name='check_different_users'),
    )
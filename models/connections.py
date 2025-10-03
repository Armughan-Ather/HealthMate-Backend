from sqlalchemy import (
    Column, Integer, Text,
    DateTime, ForeignKey, Enum, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, declarative_base, validates
from sqlalchemy.sql import func
from database import Base
from constants.enums import ConnectionTypeEnum, ConnectionStatusEnum


class Connection(Base):
    __tablename__ = 'connections'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patient_profiles.user_id', ondelete='CASCADE'), nullable=False, index=True)
    connected_user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    connection_type = Column(Enum(ConnectionTypeEnum), nullable=False)
    status = Column(Enum(ConnectionStatusEnum), nullable=False, default=ConnectionStatusEnum.PENDING)
    request_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    patient = relationship("PatientProfile", foreign_keys=[patient_id], back_populates="connections_as_patient")
    connected_user = relationship("User", foreign_keys=[connected_user_id], back_populates="connections_as_connected_user")
    
    __table_args__ = (
        CheckConstraint('patient_id != connected_user_id', name='check_no_self_connection'),
        CheckConstraint("request_message IS NULL OR LENGTH(request_message) <= 1000", name='check_request_message_length'),
        UniqueConstraint('patient_id', 'connected_user_id', 'connection_type', name='uq_patient_connection'),
        Index('idx_connection_status', 'patient_id', 'status'),
        Index('idx_connection_type_status', 'connection_type', 'status'),
    )
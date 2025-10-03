from sqlalchemy import (
    Column, Integer, Text,
    DateTime, ForeignKey, Enum, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, validates
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

    @validates('connection_type')
    def validate_connection_type(self, key, value):
        if value not in ConnectionTypeEnum:
            raise ValueError(f"Invalid connection type: {value}")
        return value
    
    @validates('patient_id')
    def validate_patient(self, key, patient_id):
        from sqlalchemy.orm import object_session
        session = object_session(self)
        if session is None:
            return patient_id
        from models.patient_profiles import PatientProfile  # adjust import path as needed
        exists = session.query(PatientProfile).filter_by(user_id=patient_id).first()
        if not exists:
            raise ValueError("Patient ID does not correspond to an existing patient profile.")
        return patient_id

    @validates('status')
    def validate_status(self, key, value):
        current_status = self.status  # might be None during INSERT

        if current_status:
            # Disallow moving from REJECTED back to PENDING
            if current_status == ConnectionStatusEnum.REJECTED and value == ConnectionStatusEnum.PENDING:
                raise ValueError("Cannot revert a rejected connection back to pending.")
            
            # Disallow moving from REVOKED to anything else
            if current_status == ConnectionStatusEnum.REVOKED and value != ConnectionStatusEnum.REVOKED:
                raise ValueError("Cannot change status after revocation.")

            # Disallow moving from ACCEPTED to PENDING or REJECTED (should be revoked instead)
            if current_status == ConnectionStatusEnum.ACCEPTED and value in {ConnectionStatusEnum.PENDING, ConnectionStatusEnum.REJECTED}:
                raise ValueError("Cannot change accepted connection back to pending or rejected.")

        return value
    
    @validates('connected_user_id')
    def validate_no_reverse_duplicate(self, key, connected_user_id):
        from sqlalchemy.orm import object_session
        session = object_session(self)
        if session is None:
            return connected_user_id  # during some operations (like bulk), session might be None

        reverse_exists = session.query(Connection).filter_by(
            patient_id=connected_user_id,
            connected_user_id=self.patient_id,
            connection_type=self.connection_type
        ).first()

        if reverse_exists:
            raise ValueError("Reverse connection already exists for this connection type.")
        return connected_user_id

    @validates('request_message')
    def validate_request_message(self, key, value):
        if value:
            trimmed = value.strip()
            if len(trimmed) == 0:
                return None  # treat empty as NULL
            if len(trimmed) > 1000:
                raise ValueError("Request message must not exceed 1000 characters.")
            return trimmed
        return value

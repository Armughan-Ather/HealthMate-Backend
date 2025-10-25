from sqlalchemy import (
    Column, Integer, DateTime, ForeignKey, Enum,
    CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, validates, object_session
from sqlalchemy.sql import func
from fastapi import HTTPException, status
from database import Base
from constants.enums import ConnectionTypeEnum, ConnectionStatusEnum


class Connection(Base):
    __tablename__ = "connections"

    # -----------------------
    # Columns
    # -----------------------
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.user_id", ondelete="CASCADE"), nullable=False)
    connected_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    connection_type = Column(Enum(ConnectionTypeEnum), nullable=False)
    status = Column(Enum(ConnectionStatusEnum), nullable=False, default=ConnectionStatusEnum.PENDING)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # -----------------------
    # Table Constraints / Indexes
    # -----------------------
    __table_args__ = (
        CheckConstraint("patient_id != connected_user_id", name="check_no_self_connection"),
        CheckConstraint("created_by_id IN (patient_id, connected_user_id)", name="check_created_by_is_participant"),
        UniqueConstraint("patient_id", "connected_user_id", "connection_type", "status", name="uq_connection_pair_type"),
        Index("idx_connections_patient_status", "patient_id", "status"),
        Index("idx_connections_connected_status", "connected_user_id", "status"),
        Index("idx_connections_type_status", "connection_type", "status"),
    )

    # -----------------------
    # Relationships
    # -----------------------
    patient = relationship("PatientProfile", foreign_keys=[patient_id], back_populates="connections_as_patient")
    connected_user = relationship("User", foreign_keys=[connected_user_id], back_populates="connections_as_connected_user")
    created_by = relationship("User", foreign_keys=[created_by_id])

    # -----------------------
    # Validators
    # -----------------------

    @validates("connection_type")
    def _validate_connection_type(self, key, value):
        """Ensure valid enum."""
        if value not in ConnectionTypeEnum:
            raise ValueError(f"Invalid connection_type: {value}")
        return value

    @validates("status")
    def _validate_status_transitions(self, key, new_status):
        """Enforce valid state transitions."""
        current = getattr(self, "status", None)
        if current is None:
            return new_status

        if current == ConnectionStatusEnum.REJECTED and new_status == ConnectionStatusEnum.PENDING:
            raise ValueError("Cannot revert REJECTED back to PENDING.")
        if current == ConnectionStatusEnum.REVOKED and new_status != ConnectionStatusEnum.REVOKED:
            raise ValueError("Cannot change status after REVOKED.")
        if current == ConnectionStatusEnum.ACCEPTED and new_status in {
            ConnectionStatusEnum.PENDING, ConnectionStatusEnum.REJECTED
        }:
            raise ValueError("Cannot change ACCEPTED back to PENDING or REJECTED; revoke instead.")
        return new_status

    @validates("patient_id", "connected_user_id")
    def _validate_participants(self, key, value):
        """
        Validate participant relationships:
        - Prevent self-connections
        - Enforce uniqueness of (patient, connected_user, type, status)
        - Prevent reverse duplicates (B→A if A→B exists)
        """
        patient_id = value if key == "patient_id" else getattr(self, "patient_id", None)
        connected_user_id = value if key == "connected_user_id" else getattr(self, "connected_user_id", None)

        if patient_id and connected_user_id and patient_id == connected_user_id:
            raise ValueError("Patient and connected user cannot be the same person.")

        session = object_session(self)
        if not session:
            return value

        connection_type = getattr(self, "connection_type", None)
        status = getattr(self, "status", None)
        if not all([patient_id, connected_user_id, connection_type, status]):
            return value

        # Normal duplicate
        exists = (
            session.query(Connection)
            .filter_by(
                patient_id=patient_id,
                connected_user_id=connected_user_id,
                connection_type=connection_type,
                status=status,
            )
            .first()
        )
        if exists:
            raise ValueError("A connection already exists between these users with the same type and status.")

        # Reverse duplicate
        reverse = (
            session.query(Connection)
            .filter_by(
                patient_id=connected_user_id,
                connected_user_id=patient_id,
                connection_type=connection_type,
                status=status,
            )
            .first()
        )
        if reverse:
            raise ValueError("A reverse connection already exists between these users with the same type and status.")

        return value

    @validates("created_by_id")
    def _validate_created_by(self, key, created_by_id):
        """Ensure creator is one of the participants."""
        patient_id = getattr(self, "patient_id", None)
        connected_user_id = getattr(self, "connected_user_id", None)
        if patient_id is not None and connected_user_id is not None:
            if created_by_id not in (patient_id, connected_user_id):
                raise ValueError("created_by_id must be either patient_id or connected_user_id.")
        return created_by_id


# from sqlalchemy import (
#     Column, Integer, Text, DateTime,
#     ForeignKey, Enum, CheckConstraint,
#     UniqueConstraint, Index
# )
# from sqlalchemy.orm import relationship, validates
# from sqlalchemy.sql import func
# from database import Base
# from constants.enums import ConnectionTypeEnum, ConnectionStatusEnum


# class Connection(Base):
#     __tablename__ = "connections"

#     id = Column(Integer, primary_key=True, index=True)
#     patient_id = Column(Integer, ForeignKey("patient_profiles.user_id", ondelete="CASCADE"), nullable=False)
#     connected_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     created_by_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

#     connection_type = Column(Enum(ConnectionTypeEnum), nullable=False)
#     status = Column(Enum(ConnectionStatusEnum), nullable=False, default=ConnectionStatusEnum.PENDING)

#     created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

#     # relationships
#     patient = relationship("PatientProfile", foreign_keys=[patient_id], back_populates="connections_as_patient")
#     connected_user = relationship("User", foreign_keys=[connected_user_id], back_populates="connections_as_connected_user")
#     created_by = relationship("User", foreign_keys=[created_by_id])

#     __table_args__ = (
#         CheckConstraint("patient_id != connected_user_id", name="check_no_self_connection"),
#         CheckConstraint("created_by_id IN (patient_id, connected_user_id)", name="check_created_by_is_participant"),
#         UniqueConstraint("patient_id", "connected_user_id", "connection_type", "status", name="uq_connection_pair_type"),
#         Index("idx_connections_patient_status", "patient_id", "status"),
#         Index("idx_connections_connected_status", "connected_user_id", "status"),
#         Index("idx_connections_type_status", "connection_type", "status"),
#     )

#     # -----------------------
#     # Validators
#     # -----------------------

#     from sqlalchemy.orm import validates, object_session
#     from sqlalchemy.exc import IntegrityError
#     from fastapi import HTTPException, status

#     @validates("connection_type")
#     def _validate_connection_type(self, key, value):
#         """Ensure valid enum type."""
#         if value not in ConnectionTypeEnum:
#             raise ValueError(f"Invalid connection_type: {value}")
#         return value


#     @validates("status")
#     def _validate_status_transitions(self, key, new_status):
#         """
#         Enforce valid state transitions:
#         - REJECTED → cannot revert to PENDING
#         - REVOKED → immutable
#         - ACCEPTED → can’t revert to PENDING/REJECTED
#         """
#         current = getattr(self, "status", None)
#         if current is None:
#             return new_status

#         if current == ConnectionStatusEnum.REJECTED and new_status == ConnectionStatusEnum.PENDING:
#             raise ValueError("Cannot revert REJECTED back to PENDING.")
#         if current == ConnectionStatusEnum.REVOKED and new_status != ConnectionStatusEnum.REVOKED:
#             raise ValueError("Cannot change status after REVOKED.")
#         if current == ConnectionStatusEnum.ACCEPTED and new_status in {
#             ConnectionStatusEnum.PENDING, ConnectionStatusEnum.REJECTED
#         }:
#             raise ValueError("Cannot change ACCEPTED back to PENDING or REJECTED; revoke instead.")
#         return new_status


#     @validates("patient_id", "connected_user_id")
#     def _validate_participants(self, key, value):
#         """
#         ✅ Combines:
#         - CheckConstraint: patient_id != connected_user_id
#         - UniqueConstraint: (patient_id, connected_user_id, connection_type, status)
#         - Reverse connection prevention
#         """
#         # --- Self-connection rule
#         patient_id = value if key == "patient_id" else getattr(self, "patient_id", None)
#         connected_user_id = value if key == "connected_user_id" else getattr(self, "connected_user_id", None)
#         if patient_id and connected_user_id and patient_id == connected_user_id:
#             raise ValueError("Patient and connected user cannot be the same person.")

#         # --- Duplicate/reverse prevention
#         from sqlalchemy.orm import object_session
#         session = object_session(self)
#         if not session:
#             return value

#         connection_type = getattr(self, "connection_type", None)
#         status = getattr(self, "status", None)
#         if not all([patient_id, connected_user_id, connection_type, status]):
#             return value

#         # Normal duplicate (A → B)
#         duplicate = (
#             session.query(Connection)
#             .filter(
#                 Connection.patient_id == patient_id,
#                 Connection.connected_user_id == connected_user_id,
#                 Connection.connection_type == connection_type,
#                 Connection.status == status,
#             )
#             .first()
#         )
#         if duplicate:
#             raise ValueError("A connection already exists between these users with the same type and status.")

#         # Reverse duplicate (B → A)
#         reverse = (
#             session.query(Connection)
#             .filter(
#                 Connection.patient_id == connected_user_id,
#                 Connection.connected_user_id == patient_id,
#                 Connection.connection_type == connection_type,
#                 Connection.status == status,
#             )
#             .first()
#         )
#         if reverse:
#             raise ValueError("A reverse connection already exists between these users with the same type and status.")

#         return value


#     @validates("created_by_id")
#     def _validate_created_by(self, key, created_by_id):
#         """
#         ✅ Mirrors CheckConstraint: created_by_id IN (patient_id, connected_user_id)
#         """
#         patient_id = getattr(self, "patient_id", None)
#         connected_user_id = getattr(self, "connected_user_id", None)
#         if patient_id is not None and connected_user_id is not None:
#             if created_by_id not in (patient_id, connected_user_id):
#                 raise ValueError("created_by_id must be either patient_id or connected_user_id.")
#         return created_by_id

#     # @validates("connection_type")
#     # def _validate_connection_type(self, key, value):
#     #     if value not in ConnectionTypeEnum:
#     #         raise ValueError(f"Invalid connection_type: {value}")
#     #     return value

#     # @validates("patient_id")
#     # def _validate_patient_exists(self, key, patient_id):
#     #     """
#     #     Ensure patient profile exists. If no session available (e.g., during migrations),
#     #     skip the DB check.
#     #     """
#     #     from sqlalchemy.orm import object_session
#     #     session = object_session(self)
#     #     if session is None:
#     #         return patient_id
#     #     from models.patient_profiles import PatientProfile
#     #     exists = session.query(PatientProfile).filter_by(user_id=patient_id).first()
#     #     if not exists:
#     #         raise ValueError("patient_id does not correspond to an existing patient profile.")
#     #     return patient_id

#     # @validates("status")
#     # def _validate_status_transitions(self, key, new_status):
#     #     """
#     #     Disallow invalid transitions:
#     #      - REJECTED -> PENDING (cannot revert)
#     #      - REVOKED -> any other (immutable after revocation)
#     #      - ACCEPTED -> PENDING/REJECTED (should be revoked instead)
#     #     """
#     #     current = getattr(self, "status", None)
#     #     if current is None:
#     #         return new_status

#     #     if current == ConnectionStatusEnum.REJECTED and new_status == ConnectionStatusEnum.PENDING:
#     #         raise ValueError("Cannot revert REJECTED back to PENDING.")
#     #     if current == ConnectionStatusEnum.REVOKED and new_status != ConnectionStatusEnum.REVOKED:
#     #         raise ValueError("Cannot change status after REVOKED.")
#     #     if current == ConnectionStatusEnum.ACCEPTED and new_status in {ConnectionStatusEnum.PENDING, ConnectionStatusEnum.REJECTED}:
#     #         raise ValueError("Cannot change ACCEPTED back to PENDING or REJECTED; revoke instead.")
#     #     return new_status

#     # @validates("connected_user_id")
#     # def _validate_no_reverse_duplicate(self, key, connected_user_id):
#     #     """
#     #     Prevent the reverse connection (A->B) when one (B->A) already exists with same type.
#     #     Skip when session is not available or required attrs not set.
#     #     """
#     #     from sqlalchemy.orm import object_session
#     #     session = object_session(self)
#     #     if session is None:
#     #         return connected_user_id

#     #     # Need patient_id and connection_type present to validate
#     #     patient_id = getattr(self, "patient_id", None)
#     #     status = getattr(self, "status", None)
#     #     connection_type = getattr(self, "connection_type", None)
#     #     if not patient_id or not connection_type or not status:
#     #         return connected_user_id

#     #     exists = session.query(Connection).filter_by(
#     #         patient_id=patient_id,
#     #         connected_user_id=connected_user_id,
#     #         connection_type=connection_type,
#     #         status=status
#     #     ).first()
#     #     if exists:
#     #         raise ValueError("Reverse connection already exists for this connection type and status.")
#     #     return connected_user_id

#     # @validates("created_by_id")
#     # def _validate_created_by_part_of_pair(self, key, created_by_id):
#     #     """
#     #     Ensure created_by is one of the participants (patient or connected_user).
#     #     If participants not available yet (object partially constructed), skip check.
#     #     """
#     #     patient_id = getattr(self, "patient_id", None)
#     #     connected_user_id = getattr(self, "connected_user_id", None)
#     #     if patient_id is None or connected_user_id is None:
#     #         return created_by_id

#     #     if created_by_id not in (patient_id, connected_user_id):
#     #         raise ValueError("created_by_id must be either patient_id or connected_user_id.")
#     #     return created_by_id
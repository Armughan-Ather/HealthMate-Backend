from typing import Optional
from sqlalchemy.orm import Session
from models.user_roles import UserRole
from constants.enums import UserRoleEnum
from models.connections import Connection
from models.patient_profiles import PatientProfile


def is_patient(user) -> bool:
    if not user:
        return False
    # user role may be in roles relationship
    for r in getattr(user, 'roles', []):
        try:
            if r.role == UserRoleEnum.PATIENT:
                return True
        except Exception:
            if str(r.role).upper() == 'PATIENT':
                return True
    return False


def is_doctor(user) -> bool:
    if not user:
        return False
    for r in getattr(user, 'roles', []):
        try:
            if r.role == UserRoleEnum.DOCTOR:
                return True
        except Exception:
            if str(r.role).upper() == 'DOCTOR':
                return True
    return False


def is_attendant(user) -> bool:
    if not user:
        return False
    for r in getattr(user, 'roles', []):
        try:
            if r.role == UserRoleEnum.ATTENDANT:
                return True
        except Exception:
            if str(r.role).upper() == 'ATTENDANT':
                return True
    return False


def is_attendant_of(db: Session, attendant_user_id: int, patient_profile_id: int) -> bool:
    # Connections table: patient_id (patient_profile_id) and connected_user_id (attendant user id)
    conn = db.query(Connection).filter(
        Connection.patient_id == patient_profile_id,
        Connection.connected_user_id == attendant_user_id,
        Connection.connection_type == 'ATTENDANT',
        Connection.status == 'ACCEPTED'
    ).first()
    return conn is not None


def is_doctor_of(db: Session, doctor_user_id: int, patient_profile_id: int) -> bool:
    conn = db.query(Connection).filter(
        Connection.patient_id == patient_profile_id,
        Connection.connected_user_id == doctor_user_id,
        Connection.connection_type == 'DOCTOR',
        Connection.status == 'ACCEPTED'
    ).first()
    return conn is not None


def can_modify_patient_logs(db: Session, actor_user, patient_profile_id: int) -> bool:
    # Patients can modify their own logs
    if actor_user is None:
        return False
    if getattr(actor_user, 'id', None) is None:
        return False
    # patient_profile_id is the PatientProfile.id; fetch profile to compare owner
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_profile_id).first()
    if patient and getattr(patient, 'user_id', None) == actor_user.id:
        return True

    # Attendants accepted for that patient can modify logs
    if is_attendant(actor_user):
        return is_attendant_of(db, actor_user.id, patient_profile_id)

    # Doctors cannot create adhoc logs (per your rules) — only patients and attendants
    return False


def can_modify_patient_schedules(db: Session, actor_user, patient_profile_id: int) -> bool:
    # Patients, attendants, and doctors can modify schedules
    if actor_user is None:
        return False
    # owner check: patient_profile.user_id should match actor_user.id
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_profile_id).first()
    if patient and getattr(patient, 'user_id', None) == actor_user.id:
        return True
    if is_attendant(actor_user) and is_attendant_of(db, actor_user.id, patient_profile_id):
        return True
    if is_doctor(actor_user) and is_doctor_of(db, actor_user.id, patient_profile_id):
        return True
    return False

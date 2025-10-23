from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta, date, time
from models.medications import Medication
from models.medication_schedules import MedicationSchedule
from models.medicines import Medicine
from .medicines import create_medicine, get_or_create_medicine
from sqlalchemy.exc import IntegrityError
from schemas.medications import MedicationUpdate, MedicationCreateWithSchedules
from fastapi import HTTPException, status
from utilities.permissions import can_modify_patient_schedules
from constants.enums import FrequencyEnum

def create_medication_core(
    db: Session,
    current_user,
    patient_profile_id: int,
    payload
):
    """
    Centralized logic for creating a medication and its schedules.
    Shared by both /me/... and /patients/{id}/... routes.
    """

    # RBAC check
    if not can_modify_patient_schedules(db, current_user, patient_profile_id):
    #if not can_modify_patient_schedules(db, current_user.id, patient_profile_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create medication for this patient."
        )

    medication = create_medication_with_schedules(
        db=db,
        patient_profile_id=patient_profile_id,
        prescribed_by=current_user.id,
        payload=payload
    )

    db.commit()
    db.refresh(medication)
    return medication

def create_medication_with_schedules(db: Session, patient_profile_id: int, prescribed_by: int, payload: MedicationCreateWithSchedules) -> Medication:
    """Create medication along with its schedules."""
    # 1️⃣ Get or create medicine
    medicine = get_or_create_medicine(db, payload.name, payload.strength, payload.form, payload.generic_name)

    if payload.duration_days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after or equal to start date."
        )

    # 3️⃣ Create medication
    medication = Medication(
        patient_profile_id=patient_profile_id,
        medicine_id=medicine.id,
        prescribed_by=prescribed_by,
        purpose=payload.purpose,
        duration_days=payload.duration_days,
        start_date=payload.start_date,
    )
    db.add(medication)
    try:
        db.flush()
    except IntegrityError as e:
        db.rollback()
        # Check if it's the unique constraint
        if 'unique_medication' in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Medication for this medicine already exists for the user."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating medication."
            )

    # 4️⃣ Create schedules
    for schedule_data in payload.schedules:
        schedule = MedicationSchedule(
            medication_id=medication.id,
            scheduled_time=schedule_data.scheduled_time,
            dosage_instruction=schedule_data.dosage_instruction
        )
        db.add(schedule)

    return medication


def count_medications(db: Session, patient_profile_id: int) -> int:
    return db.query(Medication).filter(
        Medication.patient_profile_id == patient_profile_id,
        Medication.is_active.is_(True)
    ).count()


def get_user_medicines(db: Session, patient_profile_id: int) -> List[Medicine]:
    return (
        db.query(Medicine)
        .join(Medication, Medication.medicine_id == Medicine.id)
        .filter(Medication.patient_profile_id == patient_profile_id)
        .distinct()
        .all()
    )


def get_user_medications(db: Session, patient_profile_id: int) -> List[Medication]:
    """List all medications for a patient profile."""
    return db.query(Medication).filter_by(patient_profile_id=patient_profile_id).all()


def normalize_time(t: time) -> time:
    return t.replace(second=0, microsecond=0, tzinfo=None)
def update_medication(db: Session, medication_id: int, payload: MedicationUpdate) -> Optional[Medication]:
    medication = db.query(Medication).filter_by(id=medication_id).first()
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found."
        )

    # Validate duration_days
    print('Raw payload frequency:', payload.frequency)

    if payload.duration_days is not None:
        if payload.duration_days <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duration days must be positive."
            )
        medication.duration_days = payload.duration_days

    # Update simple fields
    if payload.purpose is not None:
        medication.purpose = payload.purpose.strip() if payload.purpose.strip() else None

    if payload.start_date is not None:
        medication.start_date = payload.start_date

    if payload.frequency is not None:
        print('Updating frequency to:', payload.frequency.value)
        medication.frequency = payload.frequency.value


    if payload.custom_days is not None:
        medication.custom_days = payload.custom_days

    # Handle medication active status and sync schedules
    if payload.is_active is not None:
        medication.is_active = payload.is_active
        for sched in medication.schedules:
            sched.is_active = payload.is_active

    # Process schedules if provided
    if hasattr(payload, "schedules") and payload.schedules:
        for sched in payload.schedules:
            norm_time = normalize_time(sched.time)
            instruction = (
                sched.dosage_instruction.strip()
                if sched.dosage_instruction and sched.dosage_instruction.strip()
                else None
            )

            existing = db.query(MedicationSchedule).filter_by(
                medication_id=medication.id,
                time=norm_time
            ).first()

            if not existing:
                # ➕ New time — insert
                db.add(MedicationSchedule(
                    medication_id=medication.id,
                    time=norm_time,
                    dosage_instruction=instruction,
                    is_active=medication.is_active if medication.is_active is not None else True
                ))
            elif not existing.is_active:
                # ✅ Exists but inactive — reactivate and update instruction
                existing.is_active = True
                existing.dosage_instruction = instruction
            elif instruction is not None:
                # ✏️ Exists and active — update instruction only if provided
                existing.dosage_instruction = instruction

    # Commit changes with error handling
    try:
        db.flush()
    except IntegrityError as e:
        db.rollback()
        if 'unique_medication' in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Medication for this medicine already exists for the user."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected DB error during medication update."
        )

    return medication

# def update_medication(db: Session, medication_id: int, payload: MedicationUpdate) -> Optional[Medication]:
#     medication = db.query(Medication).filter_by(id=medication_id).first()
#     if not medication:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Medication not found."
#         )

#     # Validate dates
#     #duration_days = (payload.end_date - payload.start_date).days + 1
#     duration_days =payload.duration_days 
    
#     if duration_days <= 0:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="End date must be after or equal to start date."
#         )

#     # Get or create medicine
#     medicine = create_medicine(db, payload.name.strip(), payload.strength.strip(), payload.form.strip(), (payload.generic_name.strip() if payload.generic_name else None))

#     # Update medication fields
#     medication.medicine_id = medicine.id
#     medication.purpose = payload.purpose.strip() if payload.purpose else None
#     medication.start_date = payload.start_date
#     medication.end_date = payload.end_date
#     medication.duration_days = duration_days

#     try:
#         db.flush()
#     except IntegrityError as e:
#         db.rollback()
#         if 'unique_medication' in str(e.orig):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Medication for this medicine already exists for the user."
#             )
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Unexpected DB error during medication update."
#         )

#     # Process schedules
#     for sched in payload.schedules:
#         norm_time = normalize_time(sched.time)
#         instruction = (
#             sched.dosage_instruction.strip()
#             if sched.dosage_instruction and sched.dosage_instruction.strip()
#             else None
#         )

#         existing = db.query(MedicationSchedule).filter_by(
#             medication_id=medication.id,
#             time=norm_time
#         ).first()

#         if not existing:
#             # ➕ New time — insert
#             db.add(MedicationSchedule(
#                 medication_id=medication.id,
#                 time=norm_time,
#                 dosage_instruction=instruction,
#                 is_active=True
#             ))
#         elif not existing.is_active:
#             # ✅ Exists but inactive — reactivate and update instruction
#             existing.is_active = True
#             existing.dosage_instruction = instruction
#         elif instruction is not None:
#             # ✏️ Exists and active — update instruction only if provided
#             existing.dosage_instruction = instruction

#     db.flush()
#     return medication

# def update_medication(db: Session, medication_id: int, payload: MedicationUpdate) -> Optional[Medication]:
#     medication = db.query(Medication).filter_by(id=medication_id).first()
#     if not medication:
#         return None

#     # Update or create medicine
#     medicine = create_medicine(db, payload.name.strip(), payload.strength.strip())

#     medication.medicine_id = medicine.id
#     medication.purpose = payload.purpose.strip()
#     medication.start_date = payload.start_date
#     medication.end_date = payload.end_date
#     medication.duration_days = (payload.end_date - payload.start_date).days + 1

#     if medication.duration_days <= 0:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="End date must be after or equal to start date."
#         )

#     try:
#         db.flush()
#     except IntegrityError as e:
#         db.rollback()
#         # Check if it's the unique constraint
#         if 'unique_medication' in str(e.orig):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Medication for this medicine already exists for the user."
#             )
#         else:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="An unexpected error occurred while creating medication."
#             )

#     # Map new schedules by time
#     new_schedule_map = {sched.time: sched.dosage_instruction.strip() for sched in payload.schedules}

#     # Map existing active schedules by time
#     existing_active_schedules = {
#         sched.time: sched for sched in medication.schedules if sched.is_active
#     }

#     # 1. Update or create schedules
#     for time, new_instruction in new_schedule_map.items():
#         if time in existing_active_schedules:
#             existing_schedule = existing_active_schedules[time]
#             existing_schedule.dosage_instruction = new_instruction  # ✅ Update dosage
#         else:
#             # ➕ Add new schedule
#             new_schedule = MedicationSchedule(
#                 medication_id=medication.id,
#                 time=time,
#                 dosage_instruction=new_instruction,
#                 is_active=True
#             )
#             db.add(new_schedule)

#     # 2. Deactivate schedules not in new payload
#     new_times = set(new_schedule_map.keys())
#     for time, sched in existing_active_schedules.items():
#         if time not in new_times:
#             sched.is_active = False

#     db.flush()
#     return medication


# def delete_medication(db: Session, medication_id: int, user_id: int) -> bool:
#     """Delete a medication and its schedules."""
#     medication = db.query(Medication).filter_by(id=medication_id, user_id=user_id).first()
#     if not medication:
#         return False
#     db.delete(medication)
#     return True


def delete_medication(db: Session, medication_id: int, patient_profile_id: int) -> bool:
    """Delete a medication and its schedules."""
    medication = db.query(Medication).filter_by(id=medication_id, patient_profile_id=patient_profile_id).first()
    if not medication:
        return False
    db.delete(medication)
    return True

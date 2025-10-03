# Backend/models/__init__.py

# This file imports all models, making them available
# to SQLAlchemy and other parts of the application from a single point.
# This solves circular import and load-order issues.

from .users import User, GenderEnum
from .chats import Chat
from .messages import Message
from .medicines import Medicine
from .medications import Medication
from .medication_schedules import MedicationSchedule
from .scheduled_medication_logs import ScheduledMedicationLog
from .bp_schedules import BloodPressureSchedule
from .scheduled_bp_logs import ScheduledBPLog
from .sugar_schedules import SugarSchedule
from .scheduled_sugar_logs import ScheduledSugarLog, SugarType
from .insights import Insight, InsightPeriod

# New tables per extended schema
from .user_roles import UserRole, UserRoleEnum
from .patient_profiles import PatientProfile
from .doctor_profiles import DoctorProfile
from .connections import Connection, ConnectionTypeEnum, ConnectionStatusEnum
from .weight_logs import WeightLog
from .reminders import Reminder
from .patient_notes import PatientNote

# You can also define a __all__ variable to control what `from models import *` does, which is good practice.
__all__ = [
    "User",
    "Chat",
    "Message",
    "Medicine",
    "Medication",
    "MedicationSchedule",
    "ScheduledMedicationLog",
    "BloodPressureSchedule",
    "ScheduledBPLog",
    "SugarSchedule",
    "ScheduledSugarLog",
    "SugarType",
    "Insight",
    "InsightPeriod",
    # New
    "UserRole",
    "UserRoleEnum",
    "PatientProfile",
    "DoctorProfile",
    "GenderEnum",
    "Connection",
    "ConnectionTypeEnum",
    "ConnectionStatusEnum",
    "WeightLog",
    "Reminder",
    "PatientNote",
]
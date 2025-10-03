import enum

class RoleEnum(enum.Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ATTENDANT = "ATTENDANT"


class GenderEnum(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class ConnectionTypeEnum(enum.Enum):
    DOCTOR = "DOCTOR"
    ATTENDANT = "ATTENDANT"


class ConnectionStatusEnum(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    REVOKED = "REVOKED"


class SugarTypeEnum(enum.Enum):
    FASTING = "FASTING"
    RANDOM = "RANDOM"
    POST_MEAL = "POST_MEAL"


class InsightPeriodEnum(enum.Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class WeightUnitEnum(enum.Enum):
    KG = "KG"
    LBS = "LBS"


class FrequencyEnum(enum.Enum):
    """Frequency for schedules and reminders"""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class DayOfWeekEnum(enum.Enum):
    """Days of week for weekly schedules"""
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"
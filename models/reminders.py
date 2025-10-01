from datetime import datetime, date, time
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, ForeignKey, CheckConstraint, Text, Enum
import enum
from database import Base


class ReminderTagEnum(enum.Enum):
    APPOINTMENT = "APPOINTMENT"
    WATER = "WATER"
    EXERCISE = "EXERCISE"
    SLEEP = "SLEEP"
    MEAL = "MEAL"
    LAB_TEST = "LAB_TEST"
    THERAPY = "THERAPY"
    VACCINATION = "VACCINATION"


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tags = Column(Enum(ReminderTagEnum), nullable=False)
    topic = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    scheduled_time = Column(Time, nullable=False)
    start_date = Column(Date, nullable=False)
    duration_days = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("duration_days > 0", name="check_positive_duration"),
        CheckConstraint("LENGTH(topic) > 0", name="check_topic_not_empty"),
    )



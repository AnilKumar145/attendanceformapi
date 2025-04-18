from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('sessions.session_id', ondelete='CASCADE'))
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(15), nullable=False)
    email = Column(String(255), nullable=False)
    branch = Column(String(50), nullable=False)
    section = Column(String(10), nullable=False)
    roll_number = Column(String(20), nullable=False)
    device_info = Column(String(500))
    # Stores base64 encoded image data from webcam
    selfie_data = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    verified = Column(Boolean, default=False)
    verification_time = Column(DateTime(timezone=True))
    verified_by = Column(String(100))

    class Config:
        orm_mode = True

    def __repr__(self):
        return f"<Attendance(id={self.id}, name={self.full_name}, roll_number={self.roll_number})>"






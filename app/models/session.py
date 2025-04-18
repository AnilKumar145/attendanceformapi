from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True)
    data = Column(Text)
    created_at = Column(DateTime)
    expires_at = Column(DateTime)

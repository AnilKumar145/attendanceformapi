import logging
import base64
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.database import get_db
from app.models.attendance import Attendance
from app.models.session import Session
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

class AttendanceSubmission(BaseModel):
    session_id: str
    full_name: str
    phone_number: str
    email: EmailStr
    branch: str
    section: str
    roll_number: str
    device_info: str
    selfie_data: str

    @validator('selfie_data')
    def validate_selfie_data(cls, v):
        if not v.startswith('data:image'):
            raise ValueError('Invalid image format. Must be a base64 encoded image.')
        try:
            # Extract the base64 part after the comma
            base64_part = v.split(',')[1]
            # Try to decode to verify it's valid base64
            base64.b64decode(base64_part)
            return v
        except Exception as e:
            raise ValueError('Invalid base64 image data')

@router.post("/api/attendance/submit")
async def submit_attendance(
    submission: AttendanceSubmission,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Validate session
        session_query = select(Session).where(Session.session_id == submission.session_id)
        session_result = await db.execute(session_query)
        session = session_result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=400, detail="Invalid session")

        if session.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Session expired")

        # Create attendance record
        new_attendance = Attendance(
            session_id=submission.session_id,
            full_name=submission.full_name,
            phone_number=submission.phone_number,
            email=submission.email,
            branch=submission.branch,
            section=submission.section,
            roll_number=submission.roll_number,
            device_info=submission.device_info,
            selfie_data=submission.selfie_data,  # This will be the base64 image string
            created_at=datetime.utcnow(),
            verified=False
        )
        
        db.add(new_attendance)
        await db.commit()
        
        return {"message": "Attendance recorded successfully"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error submitting attendance: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to submit attendance")







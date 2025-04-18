from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.session import Session
import json
from typing import Dict, Optional
from pytz import timezone

class SessionManager:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.india_tz = timezone('Asia/Kolkata')

    async def validate_session(self, session_id: str) -> tuple[bool, str]:
        query = select(Session).where(Session.session_id == session_id)
        result = await self.db_session.execute(query)
        session = result.scalar_one_or_none()

        if not session:
            return False, "Session not found"

        session_data = json.loads(session.data)
        expiry_time = datetime.fromisoformat(session_data["expiry_time"])
        current_time = datetime.now(self.india_tz)

        if current_time > expiry_time:
            # Clean up expired session
            await self.db_session.execute(
                delete(Session).where(Session.session_id == session_id)
            )
            await self.db_session.commit()
            return False, "Session expired"

        return True, "Session valid"

    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session from database"""
        query = select(Session).where(Session.session_id == session_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def store_attendance(self, session_id: str, attendance_data: Dict) -> bool:
        try:
            # Get existing session
            session = await self.get_session(session_id)
            if not session:
                print(f"Session {session_id} not found")
                return False
            
            # Update the session data to include attendance
            current_data = json.loads(session.data)
            current_data['attendance'] = attendance_data
            current_data['attendance_timestamp'] = datetime.now(self.india_tz).isoformat()
            
            # Update session in database
            session.data = json.dumps(current_data)
            await self.db_session.commit()
            
            print(f"Successfully stored attendance for session {session_id}")
            return True
            
        except Exception as e:
            print(f"Error storing attendance: {str(e)}")
            await self.db_session.rollback()
            return False

    async def get_attendance_data(self, session_id: str) -> Optional[Dict]:
        """Get attendance data from session"""
        session = await self.get_session(session_id)
        if not session:
            return None
            
        session_data = json.loads(session.data)
        return session_data.get('attendance')

    async def end_session(self, session_id: str) -> bool:
        session_key = f"session:{session_id}"
        attendance_key = f"attendance:{session_id}"
        
        try:
            self.redis_client.delete(session_key, attendance_key)
            return True
        except Exception:
            return False






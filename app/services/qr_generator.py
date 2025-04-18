import qrcode
import json
import uuid
from datetime import datetime, timedelta
from pytz import timezone
from typing import Dict, Tuple
from io import BytesIO
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.session import Session

class QRGenerator:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.india_tz = timezone('Asia/Kolkata')
        self.qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

    async def generate_qr_code(self, data: str) -> BytesIO:
        """Generate QR code and store session"""
        try:
            # Generate QR image
            self.qr.clear()
            self.qr.add_data(data)
            self.qr.make(fit=True)
            img = self.qr.make_image(fill_color="black", back_color="white")
            
            # Convert to bytes
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer
            
        except Exception as e:
            print(f"Error generating QR code: {str(e)}")
            raise

    async def cleanup_expired_sessions(self):
        current_time = datetime.utcnow()
        query = delete(Session).where(Session.expires_at < current_time)
        await self.db_session.execute(query)
        await self.db_session.commit()

    async def create_new_session(self, expiry_seconds: int) -> Tuple[str, BytesIO]:
        # Cleanup expired sessions first
        await self.cleanup_expired_sessions()
        
        session_id = self.generate_session_id()
        
        # Get current time in IST
        timestamp = datetime.now(self.india_tz)
        expiry_time = timestamp + timedelta(seconds=expiry_seconds)
        
        # Create QR data with timezone info
        qr_data = {
            "session_id": session_id,
            "timestamp": timestamp.isoformat(),
            "expiry_time": expiry_time.isoformat()
        }
        
        # Convert to naive datetime for PostgreSQL storage
        new_session = Session(
            session_id=session_id,
            data=json.dumps(qr_data),
            created_at=timestamp.replace(tzinfo=None),
            expires_at=expiry_time.replace(tzinfo=None)
        )
        
        self.db_session.add(new_session)
        await self.db_session.commit()
        
        self._current_session_id = session_id
        self._current_qr_data = qr_data
        
        return session_id, self.generate_qr_code(qr_data)

    async def get_current_session(self) -> Tuple[str, Dict]:
        if not self._current_session_id or not self._current_qr_data:
            return None, None
        return self._current_session_id, self._current_qr_data







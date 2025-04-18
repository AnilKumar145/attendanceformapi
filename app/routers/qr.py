from fastapi import APIRouter, Request, Response, HTTPException, Depends
from datetime import datetime, timedelta
import uuid
from urllib.parse import quote
import logging
from app.services.qr_generator import QRGenerator
from app.services.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.session import Session
import json
router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/api/qr/generate")
async def generate_qr(
    request: Request,
    db_session: AsyncSession = Depends(get_db)
):
    try:
        attendance_form_url = "https://attendance-form-bb6b.vercel.app"
        
        # Generate session ID and expiry time
        # Increased to 3 minutes to give more buffer
        session_id = str(uuid.uuid4())
        expiry_time = datetime.utcnow() + timedelta(minutes=3)
        
        # Create session record
        session = Session(
            session_id=session_id,
            data=json.dumps({
                "session_id": session_id,
                "expiry_time": expiry_time.isoformat()
            }),
            created_at=datetime.utcnow(),
            expires_at=expiry_time
        )
        
        # Store session in database
        db_session.add(session)
        await db_session.commit()
        
        # Generate QR code URL with encoded parameters
        encoded_session_id = quote(session_id)
        encoded_expiry = quote(expiry_time.isoformat())
        attendance_url = f"{attendance_form_url}/attendance?sessionId={encoded_session_id}&expiryTime={encoded_expiry}"
        
        # Generate QR code
        qr_generator = QRGenerator(db_session=db_session)
        qr_image = await qr_generator.generate_qr_code(attendance_url)

        headers = {
            "Session-Id": session_id,
            "Expiry-Time": expiry_time.isoformat(),
            "Access-Control-Expose-Headers": "Session-Id, Expiry-Time",
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "image/png"
        }
        
        return Response(
            content=qr_image.getvalue(),
            media_type="image/png",
            headers=headers
        )
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate QR code")





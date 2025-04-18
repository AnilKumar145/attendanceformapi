from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.geolocation import GeolocationValidator
from app.utils.security import SecurityValidator
from typing import Dict
import os

router = APIRouter()

class LocationCheck(BaseModel):
    latitude: float
    longitude: float

class SecurityCheck(BaseModel):
    ip_address: str
    user_agent: str

def get_geolocation_validator():
    return GeolocationValidator(
        campus_lat=float(os.getenv('CAMPUS_LATITUDE')),
        campus_lng=float(os.getenv('CAMPUS_LONGITUDE')),
        allowed_radius=float(os.getenv('ALLOWED_RADIUS_METERS'))
    )

def get_security_validator():
    return SecurityValidator()

@router.post("/location")
async def validate_location(
    location: LocationCheck,
    geolocation_validator: GeolocationValidator = Depends(get_geolocation_validator)
) -> Dict:
    is_valid, distance = await geolocation_validator.validate_location(
        location.latitude,
        location.longitude
    )
    
    return {
        "valid": is_valid,
        "distance": round(distance, 2),
        "unit": "meters"
    }

@router.post("/security")
async def validate_security(
    security: SecurityCheck,
    security_validator: SecurityValidator = Depends(get_security_validator)
) -> Dict:
    is_vpn = await security_validator.check_vpn(security.ip_address)
    is_valid_agent = security_validator.validate_user_agent(security.user_agent)
    
    if is_vpn:
        raise HTTPException(
            status_code=400,
            detail="VPN usage detected"
        )
    
    if not is_valid_agent:
        raise HTTPException(
            status_code=400,
            detail="Invalid user agent"
        )
    
    return {"valid": True}

@router.post("/check-location")
async def check_location_before_submission(
    location: LocationCheck,
    geolocation_validator: GeolocationValidator = Depends(get_geolocation_validator)
) -> Dict:
    """
    Check if student's location is within campus bounds before allowing attendance submission
    """
    is_valid, distance = await geolocation_validator.validate_location(
        location.latitude,
        location.longitude
    )
    
    if not is_valid:
        return {
            "valid": False,
            "message": f"You are {round(distance, 2)} meters away from campus. Please ensure you are within the campus premises.",
            "distance": round(distance, 2)
        }
    
    return {
        "valid": True,
        "message": "Location verified. You can proceed with attendance submission.",
        "distance": round(distance, 2)
    }



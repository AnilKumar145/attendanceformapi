from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import app.routers.qr as qr
import app.routers.attendance as attendance
app = FastAPI()

# Update CORS settings with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",              # Local development frontend
        "http://192.168.1.4:5173",           # Local network frontend
        "https://attendance-form-pfmr.vercel.app",  # Production frontend
        "https://attendance-form-bb6b.vercel.app"   # Additional frontend domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["session-id", "expiry-time", "content-type"]
)

# Include both routers
app.include_router(qr.router)
app.include_router(attendance.router)

@app.get("/")
async def root():
    return {"message": "QR Attendance System API"}






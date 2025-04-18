# QR Attendance System Backend

FastAPI backend for QR-based attendance tracking system.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```
DATABASE_URL=postgresql+asyncpg://postgres:Anil@localhost/attendance_db
```

4. Initialize database:
```bash
alembic upgrade head
```

5. Run development server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Deployment

This application is configured for deployment on Render.com.

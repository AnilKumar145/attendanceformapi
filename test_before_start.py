import asyncio
from dotenv import load_dotenv
import os
from app.services.attendance_logger import AttendanceLogger
from datetime import datetime

async def test_sheets_connection():
    load_dotenv()
    
    # Get configuration
    credentials_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    worksheet_name = os.getenv('WORKSHEET_NAME')
    
    print(f"Testing with:")
    print(f"Credentials file: {credentials_file}")
    print(f"Spreadsheet ID: {spreadsheet_id}")
    print(f"Worksheet name: {worksheet_name}")
    
    # Initialize logger
    logger = AttendanceLogger(credentials_file, spreadsheet_id, worksheet_name)
    
    # Test data
    test_data = {
        "student_id": "TEST123",
        "name": "Test Student",
        "latitude": "0.0",
        "longitude": "0.0",
        "device_info": "Test Device",
        "distance": "0.00",
        "timestamp": datetime.now().isoformat()
    }
    
    # Try logging
    print("\nAttempting to log test data...")
    success = await logger.log_attendance(test_data)
    print(f"Test result: {'Success' if success else 'Failed'}")

if __name__ == "__main__":
    asyncio.run(test_sheets_connection())
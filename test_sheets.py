import asyncio
from dotenv import load_dotenv
import os
import json
from app.services.attendance_logger import AttendanceLogger

async def test_read_records():
    # Load environment variables
    load_dotenv()
    
    # Initialize AttendanceLogger
    logger = AttendanceLogger(
        credentials_file=os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE'),
        spreadsheet_id=os.getenv('SPREADSHEET_ID'),
        worksheet_name=os.getenv('WORKSHEET_NAME')
    )
    
    # Read all records
    records = await logger.get_attendance_records()
    print("\nAll attendance records:")
    for record in records:
        print(json.dumps(record, indent=2))

if __name__ == "__main__":
    asyncio.run(test_read_records())

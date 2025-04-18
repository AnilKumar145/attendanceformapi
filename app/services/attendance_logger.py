from datetime import datetime
from typing import Dict, List
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

try:
    from googleapiclient.errors import HttpError
except ImportError:
    raise ImportError("Please ensure google-api-python-client is installed by running: pip install google-api-python-client")

class AttendanceLogger:
    def __init__(self, credentials_file: str, spreadsheet_id: str, worksheet_name: str):
        self.spreadsheet_id = spreadsheet_id
        self.worksheet_name = worksheet_name
        self.credentials = self._get_credentials(credentials_file)
        self.service = build('sheets', 'v4', credentials=self.credentials)

    def _get_credentials(self, credentials_file: str):
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        return service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=scopes
        )

    async def log_attendance(self, attendance_data: Dict) -> bool:
        try:
            print("\n=== Google Sheets Logging Details ===")
            print(f"Spreadsheet ID: {self.spreadsheet_id}")
            print(f"Worksheet Name: {self.worksheet_name}")
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row_data = [
                timestamp,
                attendance_data.get('student_id', ''),
                attendance_data.get('name', ''),
                attendance_data.get('latitude', ''),
                attendance_data.get('longitude', ''),
                attendance_data.get('distance', ''),
                attendance_data.get('device_info', '')
            ]
            
            print("\nRow data to be inserted:")
            print(json.dumps(row_data, indent=2))

            range_name = f"{self.worksheet_name}!A:G"
            body = {
                'values': [row_data]
            }

            print("\nExecuting Google Sheets API call...")
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            print("\nAPI Response:")
            print(json.dumps(result, indent=2))

            return True

        except Exception as e:
            print("\n=== ERROR in log_attendance ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print(f"Error details: {getattr(e, 'detail', 'No additional details')}")
            return False

    async def get_attendance_records(self, date: str = None) -> List[Dict]:
        try:
            range_name = f"{self.worksheet_name}!A:G"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()

            rows = result.get('values', [])
            if not rows:
                return []

            headers = ['timestamp', 'student_id', 'name', 'latitude', 'longitude', 'distance', 'device_info']
            records = []

            for row in rows[1:]:  # Skip header row
                if len(row) < len(headers):
                    row.extend([''] * (len(headers) - len(row)))
                record = dict(zip(headers, row))
                
                if date:
                    row_date = record['timestamp'].split()[0]
                    if row_date != date:
                        continue
                        
                records.append(record)

            return records

        except HttpError as error:
            print(f"An error occurred: {error}")
            return []






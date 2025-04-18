from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import List, Optional
import os

class GoogleSheetsClient:
    def __init__(self):
        self.credentials = self._get_credentials()
        self.service = build('sheets', 'v4', credentials=self.credentials)

    def _get_credentials(self) -> Credentials:
        creds_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        
        return service_account.Credentials.from_service_account_file(
            creds_file,
            scopes=scopes
        )

    def create_sheet(self, spreadsheet_id: str, sheet_name: str) -> bool:
        try:
            body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name,
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 10
                            }
                        }
                    }
                }]
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            # Add headers
            headers = [
                'Timestamp',
                'Student ID',
                'Name',
                'Latitude',
                'Longitude',
                'Distance',
                'Device Info'
            ]
            
            self.update_range(
                spreadsheet_id,
                f'{sheet_name}!A1:G1',
                [headers]
            )
            
            return True
        except Exception as e:
            print(f"Error creating sheet: {e}")
            return False

    def update_range(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[List]
    ) -> bool:
        try:
            body = {'values': values}
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            return True
        except Exception as e:
            print(f"Error updating range: {e}")
            return False

    def get_range(
        self,
        spreadsheet_id: str,
        range_name: str
    ) -> Optional[List[List]]:
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            return result.get('values', [])
        except Exception as e:
            print(f"Error getting range: {e}")
            return None
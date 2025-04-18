from dotenv import load_dotenv
import os
from app.utils.google_sheets import GoogleSheetsClient

def create_worksheet():
    # Load environment variables
    load_dotenv()
    
    # Initialize the client
    client = GoogleSheetsClient()
    
    # Get spreadsheet ID and worksheet name from env
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    worksheet_name = os.getenv('WORKSHEET_NAME')
    
    # Create the worksheet
    success = client.create_sheet(spreadsheet_id, worksheet_name)
    if success:
        print(f"Successfully created worksheet: {worksheet_name}")
    else:
        print("Failed to create worksheet")

if __name__ == "__main__":
    create_worksheet()
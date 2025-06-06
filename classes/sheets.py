from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os
import ast
from datetime import datetime
from typing import Final

SHEET_NAME = os.getenv("SHEET_NAME")

SCOPES: Final = [
    "https://www.googleapis.com/auth/spreadsheets",
    # "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

CREDENTIALS: Final = ServiceAccountCredentials.from_json_keyfile_name(
    "secrets/sheets_api.json", SCOPES
)

CLIENT: Final = gspread.authorize(CREDENTIALS)

DATA: Final = CLIENT.open(SHEET_NAME)
VARIABLES: Final = DATA.get_worksheet(0)

def get_all_ids() -> list:
    return VARIABLES.col_values(1)

class CCell:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def get(self) -> str: # % Ίσως το get() μπορεί να επιστρέφει όλα τα types σύμφωνα με καποιο cell_type value
        if VARIABLES.cell(self.row, self.col).value is None:
            return "None"
        else:
            return VARIABLES.cell(self.row, self.col).value.strip()

    def get_float(self) -> float|None:
        try:
            return float(self.get())
        except ValueError:
            return None
    
    def get_dict(self) -> dict:
        try:
            return ast.literal_eval(self.get())
        except ValueError:
            return {}

    def get_time(self) -> datetime:
        try:    #!FIXME
            time = self.get()
            print(time)
            return datetime.strptime(time, "%Y/%m/%d %H:%M:%S")
        except ValueError:
            return None

    def set(self, value: str | float | int | dict | datetime):
        print(str(value))
        VARIABLES.update_cell(self.row, self.col, str(value))

    def round(self):
        rounded = round(self.get_float(), 1)
        self.set(rounded)

from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os

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

DATA: Final = CLIENT.open("GamblersUniversity")
VARIABLES: Final = DATA.get_worksheet(0)


class CCell:  # * Το μόνο πράγμα που μπορεί να αλλάξει είναι να βγει το round και τα comments.
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def get(self) -> str:
        if VARIABLES.cell(self.row, self.col).value is None:
            return "None"
        else:
            return VARIABLES.cell(self.row, self.col).value.strip()

    def get_float(self) -> float:
        try:
            return float(self.get())
        except ValueError:
            return 0

    def set(self, value: str | float | int):
        VARIABLES.update_cell(self.row, self.col, str(value))

    def round(self):
        rounded = round(self.get_float(), 1)
        self.set(rounded)




class User:
    def __init__(self, user_id:int):
        self.user_id = user_id
        ids = VARIABLES.col_values(1)
        row = ids.index(str(user_id)) + 1
        self.balance = CCell(row, 2)


def register_user(user_id:int):
    ids = VARIABLES.col_values(1)
    print(ids)
    if not str(user_id) in ids:
        temp_cell = CCell(len(ids)+1, 1)
        temp_cell.set(user_id)
        all_users.append(User(user_id))
    else:
        raise UserAlreadyRegistered
    

def generate_user_objects():
    global all_users
    all_users = []
    ids = VARIABLES.col_values(1)
    for id in ids:
        all_users.append(User(id))


def get_user(key_id) -> User:
    for user in all_users:
        if str(user.user_id) == str(key_id):
            return user
    return None



class UserAlreadyRegistered(Exception):
    def __init__(self, *args):
        super().__init__(*args)

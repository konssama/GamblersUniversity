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
    "sheets_api.json", SCOPES
)

CLIENT: Final = gspread.authorize(CREDENTIALS)

DATA: Final = CLIENT.open("GamblersUniversity")
VARIABLES: Final = DATA.get_worksheet(0)
# ARCHIVE: Final = DATA.get_worksheet(1)
# SETTINGS: Final = DATA.get_worksheet(2)
# JOKES: Final = DATA.get_worksheet(3)

class CCell:  # * Το μόνο πράγμα που μπορεί να αλλάξει είναι να βγει το round και τα comments.
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def get(self) -> str:
        if VARIABLES.cell(self.row, self.col).value is None:
            return "None"
        else:
            return VARIABLES.cell(self.row, self.col).value.strip()

    def getFloat(self) -> float:
        try:
            return float(self.get())
        except ValueError:
            return 0

    def set(self, value: str | float | int):
        print(value)
        VARIABLES.update_cell(self.row, self.col, value)

    def round(self):
        rounded = round(self.getFloat(), 1)
        self.set(rounded)


class RRow:
    def __init__(self, row: int, index: CCell):
        self.row = row
        self.index = index

    def getIndex(self) -> int:  # *Should not be used outside of class
        return int(self.index.getFloat())

    def append(self, value: str | float):
        self.index.set(self.getIndex() + 1)
        VARIABLES.update_cell(self.row, self.getIndex(), value)

    def remove(self, value: str):
        tempList = self.getList()
        tempList.remove(value)

        self.setList(tempList)

    def empty(self):
        self.index.set(0)
        VARIABLES.delete_rows(self.row)
        VARIABLES.insert_row([], self.row)

    def length(self) -> int:
        return len(VARIABLES.row_values(self.row))

    def getList(self) -> list[str]:
        return VARIABLES.row_values(self.row)

    def setList(self, arr: list):
        VARIABLES.delete_rows(self.row)
        VARIABLES.insert_row(arr, self.row)
        self.index.set(len(arr))


# class SSetting:  # * Το μόνο πράγμα που μπορεί να αλλάξει είναι να βγει το round και τα comments.
#     def __init__(self, row: int, col: int):
#         self.row = row
#         self.col = col

#     def get(self) -> str:
#         if SETTINGS.cell(self.row, self.col).value is None:
#             return "None"
#         else:
#             return SETTINGS.cell(self.row, self.col).value.strip()

#     def getFloat(self) -> float:
#         try:
#             return float(self.get())
#         except ValueError:
#             return 0

#     def set(self, value: str | float | int):
#         SETTINGS.update_cell(self.row, self.col, value)
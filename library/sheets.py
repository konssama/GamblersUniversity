import ast
import os
from datetime import datetime
from typing import Final

import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()
is_prod = True if os.getenv("ENV") == "PROD" else False
SHEET_NAME = os.getenv("SHEET_NAME_PROD") if is_prod else os.getenv("SHEET_NAME_TEST")

SCOPES: Final = [
    "https://www.googleapis.com/auth/spreadsheets",
    # "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

CREDENTIALS: Final = ServiceAccountCredentials.from_json_keyfile_name(
    "secrets/sheets_api.json", SCOPES
)

CLIENT: Final = gspread.authorize(CREDENTIALS)

DATA: Final = CLIENT.open(SHEET_NAME)
VARIABLES: Final = DATA.get_worksheet(0)


def get_all_ids() -> list[str]:
    return VARIABLES.col_values(1)


def type_parse(value_type: str, value: str):
    try:
        match value_type:
            case "str":
                return value
            case "float":
                return round(float(value), 2)
            case "int":
                # doing this weird two part cast cause int(value) raised a ValueError
                return int(round(float(value), 2))
            case "dict":
                return ast.literal_eval(value)
            case "datetime":
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S%z")
    except ValueError:
        print(f"Cell error: Tried to read value {value} as a {value_type}")


def generate_call_queues():
    global _get_queue
    _get_queue = []
    global _set_queue
    _set_queue = []


def pop_get_queue() -> list:
    if len(_get_queue) == 0:
        return []

    cells: list[str] = []  # cell coords in C9 format
    types: list[str] = []  # type[i] is the intended type for cells[i]

    # translate _get_queue pairs in a [A1,B12] cell notation cause that's what batch_get() wants
    for row, col, value_type in _get_queue:
        cell = gspread.utils.rowcol_to_a1(row, col)
        cells.append(cell)
        types.append(value_type)

    _get_queue.clear()
    response = VARIABLES.batch_get(cells)

    parsed_values = []
    for i in range(len(response)):
        # weird ahh syntax cause batch_get returns things as [[['0']], [['2025-06-09 20:27:49']]]
        parsed_values.append(type_parse(types[i], response[i][0][0]))

    return parsed_values


def push_set_queue():
    if len(_set_queue) == 0:
        return

    batch_data = []
    for row, col, value in _set_queue:
        if isinstance(value, float):
            value = round(value, 2)

        new_dict = {
            "range": gspread.utils.rowcol_to_a1(row, col),
            "values": [[str(value)]],
        }

        batch_data.append(new_dict)

    _set_queue.clear()
    VARIABLES.batch_update(batch_data)


class CCell:
    def __init__(self, value_type: str, row: int, col: int):
        if value_type in ["str", "float", "int", "dict", "datetime"]:
            self.value_type = value_type
        else:
            print(f"Cell {row},{col}: {value_type} is not a recognized type")

        self.row = row
        self.col = col

    def set(self, value: str | float | int | dict | datetime):
        if value is float:
            value = round(value, 2)

        VARIABLES.update_cell(self.row, self.col, str(value))

    def get(self) -> str | float | int | dict | datetime:
        value = VARIABLES.cell(self.row, self.col).value.strip()
        return type_parse(self.value_type, value)

    def next_value(self, value):
        _set_queue.append([self.row, self.col, value])

    def queue_value(self):
        _get_queue.append([self.row, self.col, self.value_type])

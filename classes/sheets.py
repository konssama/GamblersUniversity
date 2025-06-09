import ast
import os
from datetime import datetime
from typing import Final
from dotenv import load_dotenv
import gspread
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


def get_all_ids() -> list:
    return VARIABLES.col_values(1)


def type_parse(value_type, value):
    try:
        match value_type:
            case "str":
                return value
            case "float":
                return float(value)
            case "int":
                return int(value)
            case "dict":
                return ast.literal_eval(value)
            case "datetime":
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print(f"Cell error: Tried to push value {value} to a cell of type {value_type}")


def generate_call_queues():
    global _get_queue
    _get_queue = []
    global _set_queue
    _set_queue = []


def pop_get_queue() -> list:
    cells = []
    types = []

    # translate _get_queue pairs in a [A1,B12] cell notation cause that's what batch_get() wants
    for row, col, value_type in _get_queue:  # noqa: F823 ignore error this will have been created by generate_call_queues() at the start
        cell = gspread.utils.rowcol_to_a1(row, col)
        cells.append(cell)
        types.append(value_type)

    _get_queue = []
    str_values = VARIABLES.batch_get(cells)

    parsed_values = []
    for i in range(len(str_values)):
        parsed_values.append(type_parse(types[i], str_values[i]))

    return parsed_values


def push_set_queue():
    batch_data = []
    for row, col, value in _set_queue:  # noqa: F823 ignore error this will have been created by generate_call_queues() at the start
        new_dict = {"range": gspread.utils.rowcol_to_a1(row, col), "values": [[value]]}
        batch_data.append(new_dict)

    _set_queue = []
    VARIABLES.batch_update(batch_data)


class CCell:
    def __init__(self, value_type: str, row: int, col: int):
        if value_type in ["str", "float", "int", "dict", "datetime"]:
            self.value_type = value_type
        else:
            print(f"{value_type} is not a recognized type")

        self.row = row
        self.col = col

    def queue_value(self):
        _get_queue.append([self.row, self.col, self.value_type])

    def next_value(self, value):
        _set_queue.append([self.row, self.col, value])

    def set(self, value: str | float | int | dict | datetime):
        VARIABLES.update_cell(self.row, self.col, str(value))

    def get(self) -> str | float | int | dict | datetime:
        value = VARIABLES.cell(self.row, self.col).value.strip()
        return type_parse(self.value_type, value)

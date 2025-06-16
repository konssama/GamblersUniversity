from classes.sheets import CCell, get_all_ids, push_set_queue
from classes.time_module import get_timestamp


class User:
    def __init__(self, user_id: int, is_new: bool = False, id_cache: list = []):
        # when creating the heap of objects in mass we can get the ids in one call and pass them for easy access
        if len(id_cache) == 0:
            ids = get_all_ids()
        else:
            ids = id_cache

        if is_new:
            row = len(ids) + 1
            temp_cell = CCell("int", row, 1)  # temp cell to just write to the database
            temp_cell.set(user_id)
        else:
            # this can not cause an exception cause we checked that it existed
            # in register_user() before and we called with is_new=True if it did not
            # the other case is the heap creation, in which we call the constructor
            # with the ids that are already in the spreadsheet
            row = ids.index(str(user_id)) + 1

        self.row = row

        # just store the id as an int cause it's not going to change
        self.user_id = user_id

        self.balance = CCell("float", row, 2)
        self.last_cashout = CCell("datetime", row, 3)
        self.gpu_count = CCell("int", row, 4)

        if is_new:
            self.balance.next_value(0)
            self.last_cashout.next_value(get_timestamp())
            self.gpu_count.next_value(1)
            push_set_queue()

    # used to restore id if the spreadsheet was damaged
    # note that this need to have the bot running with the id/row pairs matched correctly
    def refresh_id(self, user_id: int):
        temp_cell = CCell("int", self.row, 1)
        temp_cell.set(user_id)


def register_user(user_id: int):
    ids = get_all_ids()
    if str(user_id) not in ids:
        _all_users.append(User(user_id, is_new=True, id_cache=ids))
    else:
        raise UserAlreadyRegistered


def generate_user_objects():
    global _all_users
    _all_users = []
    ids = get_all_ids()
    for id in ids:
        _all_users.append(User(id, id_cache=ids))


def get_user(key_id: int) -> User:
    for user in _all_users:
        if str(user.user_id) == str(key_id):
            return user

    print(f"User with id {key_id} not found.")
    return None


def get_all_users():
    return _all_users


class UserAlreadyRegistered(Exception):
    def __init__(self, *args):
        super().__init__(*args)

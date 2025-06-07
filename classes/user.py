from datetime import datetime

from classes.sheets import CCell, get_all_ids


class User:
    def __init__(self, user_id:int, is_new:bool=False):
        self.user_id = user_id

        ids = get_all_ids()
        row = ids.index(str(user_id)) + 1

        self.balance = CCell(row, 2)
        self.last_cashout = CCell(row, 3)
        self.gpu_count = CCell(row, 4)

        if is_new:
            self.balance.set(0)
            self.last_cashout.set(datetime.now().replace(microsecond=0))
            self.gpu_count = 0


def register_user(user_id:int):
    ids = get_all_ids()
    if str(user_id) not in ids:
        temp_cell = CCell(len(ids)+1, 1)
        temp_cell.set(user_id)
        all_users.append(User(user_id, is_new=True))
    else:
        raise UserAlreadyRegistered


def generate_user_objects():
    global all_users
    all_users = [] # * νομίζω δέν δουλεύει σωστά
    ids = get_all_ids()
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

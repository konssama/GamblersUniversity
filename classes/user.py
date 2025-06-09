from datetime import datetime

from classes.sheets import CCell, get_all_ids, push_set_queue


class User:
    def __init__(self, user_id: int, is_new: bool = False, id_cache: list = []):
        self.user_id = user_id

        if len(id_cache) == 0:
            ids = get_all_ids()
            row = ids.index(str(user_id)) + 1
        else:  # when creating the heap of objects in mass we can get the ids in one call and pass them for easy access
            ids = id_cache
            row = ids.index(str(user_id)) + 1

        self.balance = CCell("float", row, 2)
        self.last_cashout = CCell("datetime", row, 3)
        self.gpu_count = CCell("int", row, 4)

        if is_new:  # % make batch set optimization after testing that it works
            self.balance.set(0)
            self.last_cashout.set(datetime.now().replace(microsecond=0))
            self.gpu_count.set(0)


def register_user(user_id: int):
    ids = get_all_ids()
    if str(user_id) not in ids:
        temp_cell = CCell("int", len(ids) + 1, 1)
        temp_cell.set(user_id)
        _all_users.append(User(user_id, is_new=True, id_cache=ids))
    else:
        raise UserAlreadyRegistered


def generate_user_objects():
    global _all_users
    _all_users = []
    ids = get_all_ids()
    for id in ids:
        _all_users.append(User(id, id_cache=ids))


def get_user(key_id) -> User:
    for user in _all_users:
        if str(user.user_id) == str(key_id):
            return user
    return None


def get_all_users():
    return _all_users


class UserAlreadyRegistered(Exception):
    def __init__(self, *args):
        super().__init__(*args)

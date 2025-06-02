from sheets import CCell, get_all_ids

class User:
    def __init__(self, user_id:int):
        self.user_id = user_id
        ids = get_all_ids()
        row = ids.index(str(user_id)) + 1
        self.balance = CCell(row, 2)


def register_user(user_id:int):
    ids = get_all_ids()
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

from library.sheets import CCell, get_all_ids, push_set_queue, pop_get_queue
from library.time_module import get_timestamp


class User:
    def __init__(
        self,
        user_id: int,
        is_new: bool = False,
        user_name: str = "",
        id_cache: list = [],
    ):
        """
        Parameters
        -----------
        user_id: :class:`int`
            The discord id of the user.
        is_new: :class:`bool`
            Use when the user if registering in the database for the first time.
            Default: False
        user_name: :class:`str`
            The discord name of the user. This value is ignored if ``is_new==False``.
            Default: ""
        id_cache: :class:`list`
            A list of all the ids in the database. If you have them in a var pass them here to not refetch them again and again.
            Default: []
        """
        # when creating the heap of objects in mass we can get the ids in one call and pass them for easy access
        if len(id_cache) == 0:
            ids = get_all_ids()
        else:
            ids = id_cache

        if is_new:
            row = len(ids) + 1
            # temp_cell = CCell("int", row, 1)  # temp cell to just write to the database
            # temp_cell.set(user_id)
        else:
            # this can not cause an exception cause we checked that it existed
            # in register_user() before and we called with is_new=True if it did not
            # the other case is the heap creation, in which we call the constructor
            # with the ids that are already in the spreadsheet
            row = ids.index(str(user_id)) + 1

        self.row = row

        # just store the id as an int cause it's not going to change
        self.user_id = user_id
        self.id_cell = CCell("int", row, 1)

        self.name_cell = CCell("str", row, 2)
        self.last_activity = CCell("datetime", row, 3)
        self.balance = CCell("float", row, 4)
        self.last_cashout = CCell("datetime", row, 5)
        self.gpu_count = CCell("int", row, 6)

        if is_new:
            self.id_cell.next_value(user_id)

            # lets also keep tha name in the database for more readability
            self.name = user_name
            self.name_cell.next_value(user_name)

            now = get_timestamp()
            self.last_activity.next_value(now)
            self.balance.next_value(0)
            self.last_cashout.next_value(now)
            self.gpu_count.next_value(1)
            push_set_queue()
        else:  # if we have a set name save it in memory since it's not going to change much
            self.name = self.name_cell.get()


def register_user(user_id: int, user_name: str):
    ids = get_all_ids()
    if str(user_id) not in ids:
        _all_users.append(User(user_id, is_new=True, id_cache=ids, user_name=user_name))
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


def get_all_users() -> list[User]:
    return _all_users


def get_all_users_sorted(key: str) -> list[User]:
    """
    Parameters
    -----------
    key: :class:`str`
        Sort users based on:
        `"balance"`
    """
    users = get_all_users()

    match key:
        case "balance":
            for user in users:
                user.balance.queue_value()

            sorting_list = pop_get_queue()

        case _:
            print(f"sort type: {key} not found. returning unsorted list")

    # some actual chicanery claude did to sort both lists together by key
    # you can't tell me python is readable smh
    sorted_pairs = sorted(zip(users, sorting_list), key=lambda x: x[1], reverse=True)
    sorted_users = [pair[0] for pair in sorted_pairs]

    return sorted_users


class UserAlreadyRegistered(Exception):
    def __init__(self, *args):
        super().__init__(*args)

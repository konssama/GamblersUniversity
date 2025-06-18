from library.sheets import pop_get_queue, push_set_queue
from library.user import User


def calc_gpu_price(current_amount: int, buying_amount: int) -> float:
    BASE_PRICE = 100
    SCALING_FACTOR = 2.2

    total_price = 0

    for i in range(buying_amount):
        gpu_number = current_amount + i + 1

        gpu_price = BASE_PRICE * (SCALING_FACTOR ** (gpu_number - 1))
        gpu_price = round(gpu_price, 2)
        total_price += gpu_price

    # the total cost for 9 gpus is 221149.35 with scaling 2.2 and base price 100
    total_price = round(total_price, 2)
    return total_price


def buy_gpus(user: User, amount: int) -> str:
    user.gpu_count.queue_value()
    user.balance.queue_value()
    gpus, current_balance = pop_get_queue()

    if gpus >= 10:  # more not possible cause we clamp each time we buy
        return "Έχεις ήδη το max των 10 gpu."

    if gpus + amount > 10:
        # decrease the bought amount to fit withing 10 gpu limit
        amount = 10 - gpus

    total_gpu_price = calc_gpu_price(gpus, amount)

    if total_gpu_price > current_balance:
        return f"Δεν έχεις αρκετά χρήματα. Χρειάζεσαι {total_gpu_price}€."

    gpus += amount
    current_balance -= total_gpu_price

    user.gpu_count.next_value(gpus)
    user.balance.next_value(current_balance)
    push_set_queue()

    if gpus == 10:
        return f"Όκε αγόρασες {amount} gpu και έχεις φτάσει το max των 10 gpu. Πλήρωσες {total_gpu_price}€."

    return f"Όκε έχεις {gpus} gpu. Πλήρωσες {total_gpu_price}€."


def handle_buy_command(user: User, item: str, amount: int) -> str:
    # assume that amount has been checked as a non 0 positive integer
    match item:
        case "gpu" | "gpus":
            return buy_gpus(user, amount)
        case _:
            raise BoughtItemNotFound


class BoughtItemNotFound(Exception):
    def __init__(self, *args):
        super().__init__(*args)

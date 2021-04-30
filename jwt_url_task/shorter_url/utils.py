import string
from secrets import choice


def create_new_url():
    return "".join([choice(string.ascii_letters) for _ in range(5)])

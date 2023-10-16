from ...utils import get_random_secret_key
from .. import Field


class PasswordField(Field):
    def from_db_value(self, value: str):
        return get_random_secret_key()

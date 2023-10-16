from . import Field


class JsonField(Field):
    def from_db_value(self, value: str):
        import json

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

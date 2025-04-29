
class Storage:
    def __init__(self):
        self.store: dict[int, str] = {}
        pass

    def contains(self, key: int) -> bool:
        return key in self.store

    def try_get_value(self, key):
        pass

    def get(self, key):
        return self.store[key]

    def get_time_stamp(self, key):
        pass

    def set(self, key, value, expiration_time = 0):
        self.store[key] = value

    def get_expiration_time(self, key):
        pass

    def remove(self, key):
        pass

    def touch(self, key):
        pass
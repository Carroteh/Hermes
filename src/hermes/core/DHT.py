

class DHT:
    def __init__(self):
        self._router = None

    @property
    def router(self):
        return self._router

    @router.setter
    def router(self, value):
        self._router = value



class RPCError:
    def __init__(self):
        self.timeout_error: bool = False
        self.id_mismatched_error: bool = False
        self.peer_error: bool = False
        self.protocol_error: bool = False
        self.peer_error_message: str = ""
        self.protocol_error_message: str = ""

    def has_error(self) -> bool:
        return self.timeout_error or self.id_mismatched_error or self.peer_error or self.protocol_error



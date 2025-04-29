
class RPCError:
    def __init__(
            self,
            timeout_error: bool = False,
            id_mismatched_error: bool = False,
            peer_error: bool = False,
            protocol_error: bool = False,
            peer_error_message: str = '',
            protocol_error_message: str = '',
        ):
        self.timeout_error: bool = timeout_error
        self.id_mismatched_error: bool = id_mismatched_error
        self.peer_error: bool = peer_error
        self.protocol_error: bool = protocol_error
        self.peer_error_message: str = peer_error_message
        self.protocol_error_message: str = protocol_error_message

    def has_error(self) -> bool:
        return self.timeout_error or self.id_mismatched_error or self.peer_error or self.protocol_error



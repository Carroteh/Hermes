class Error:
    def __init__(
            self,
            user_doesnt_exist: bool = False,
            nickname_already_in_use: bool = False,
            isolated: bool = False,
            query_with_self: bool = False,
            not_registered: bool = False,
            already_registered: bool = False,
            error_message: str = '',
        ):
        self.isolated: bool = isolated
        self.query_with_self: bool = query_with_self
        self.not_registered: bool = not_registered
        self.already_registered: bool = already_registered
        self.nickname_already_in_use: bool = nickname_already_in_use
        self.user_doesnt_exist: bool = user_doesnt_exist
        self.error_message: str = error_message

    def has_error(self) -> bool:
        return self.user_doesnt_exist or self.nickname_already_in_use or self.already_registered or self.not_registered or self.query_with_self or self.isolated
class Error:
    def __init__(
            self,
            user_doesnt_exist: bool = False,
            nickname_already_in_use: bool = False,
            error_message: str = '',
        ):
        self.nickname_already_in_use: bool = nickname_already_in_use
        self.user_doesnt_exist: bool = user_doesnt_exist
        self.error_message: str = error_message

    def has_error(self) -> bool:
        return self.user_doesnt_exist or self.nickname_already_in_use
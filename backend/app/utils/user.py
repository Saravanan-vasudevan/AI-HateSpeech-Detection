class User:
    '''
    Representation of a user, whether regular
    user or admin
    '''
    __username__   = None
    __first_name__ = None
    __last_name__  = None
    __admin__      = None

    def __init__(self, username : str, first_name : str,
                 last_name : str, admin : bool = False) -> None:
        self.__username__   = username
        self.__first_name__ = first_name
        self.__last_name__  = last_name
        self.__admin__      = admin

    def __str__(self) -> str:
        if self.__admin__:
            return f'User (admin) - {self.__username__}: {self.__first_name__} {self.__last_name__}'

        else:
            return f'User (user) - {self.__username__}: {self.__first_name__} {self.__last_name__}'

    def __repr__(self) -> str:
        object_name = type(self).__name__

        object_str  = self.__str__()

        return f'{object_name} ({object_str})'

    def is_admin(self) -> bool:
        return self.__admin__

    def get_username(self) -> str:
        return self.__username__

    def get_name(self) -> str:
        first = self.__first_name__ if self.__first_name__ is not None else ''
        last = self.__last_name__ if self.__last_name__ is not None else ''

        full_name = f'{first} {last}'.strip()

        return full_name if full_name else None

    def to_dict(self) -> dict:
        return {
            'username'   : self.get_username(),
            'first_name' : self.__first_name__,
            'last_name'  : self.__last_name__,
            'admin'      : self.__admin__,
            'full_name'  : self.get_name()
        }
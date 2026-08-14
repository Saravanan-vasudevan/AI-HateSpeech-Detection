class User:
    '''
    Representation of a user, whether regular
    user or admin
    '''
    # Properties of the user
    __username__   = None   # User's username
    __first_name__ = None   # User's first name
    __last_name__  = None   # User's last name
    __admin__      = None   # Where user is password

    def __init__(self, username : str, first_name : str, 
                 last_name : str, admin : bool = False) -> None:
        '''
        Creates the user role

        Input args:
        - username (str)   : Username of the user
        - first_name (str) : User's first name
        - last_name  (str) : User's last name
        - admin (bool)     : Whether us is an admin
        '''
        # Storing user's attributes
        self.__username__   = username
        self.__first_name__ = first_name
        self.__last_name__  = last_name
        self.__admin__      = admin

    def __str__(self) -> str:
        '''
        String representation of the user

        Input args:
        - None

        Return:
        - (str) : Representation of the object
        '''
        # Checking if user is an admin
        if self.__admin__:
            return f'User (admin) - {self.__username__}: {self.__first_name__} {self.__last_name__}'

        # Else, Returning regular user
        else:
            return f'User (user) - {self.__username__}: {self.__first_name__} {self.__last_name__}'
    
    def __repr__(self) -> str:
        '''
        Helpful representation of the object
        that has been created

        Input args:
        - None

        Return:
        - (str) : String representation of the object
        '''
        # Retrieving the object type
        object_name = type(self).__name__

        # Retrieving string of this object
        object_str  = self.__str__()

        # Creating the stirng object
        return f'{object_name} ({object_str})'
    
    def is_admin(self) -> bool:
        '''
        Determines if the user is an admin user

        Input args:
        - None

        Return:
        - (bool) : True if user is an admin
        '''
        return self.__admin__
    
    def get_username(self) -> str:
        '''
        Retrieves the username of the user

        Input args:
        - None

        Return:
        - (str) : Username of the user
        '''
        return self.__username__
    
    def get_name(self) -> str:
        '''
        Retrieves the name of the user

        Input args:
        - None

        Return:
        - (str) : First name and last name
        '''
        # Retrieving the names
        first = self.__first_name__ if self.__first_name__ is not None else ''
        last = self.__last_name__ if self.__last_name__ is not None else ''

        # Concatenating the name
        full_name = f'{first} {last}'.strip() 

        # Returning option with none
        return full_name if full_name else None 
    
    def to_dict(self) -> dict:
        '''
        Creates a dictionary representation of the user
        This is crucial to interacting with the object

        Input args:
        - None

        Return:
        - dict
        '''
        # Returning a dictionary representation
        return {
            'username'   : self.get_username(),
            'first_name' : self.__first_name__,
            'last_name'  : self.__last_name__,
            'admin'      : self.__admin__,
            'full_name'  : self.get_name() 
        }
from pydantic import BaseModel, constr


class Role:
    CUSTOMER = 'customer'
    ADMIN = 'admin'


TUsername = constr(pattern='^\w{2,30}$')


class LoginData(BaseModel):
    username: TUsername
    password: str


class User(BaseModel):
    id: int | None = None
    username: TUsername
    password: str
    role: str


    def is_customer(self):
        ''' Compares the user's role if it's a customer when a JWT token is written in the Header.
        
        Returns:
            - True/False
        '''

        return self.role == Role.CUSTOMER
    

    def is_admin(self):
        ''' Compares the user's role if it's an admin when a JWT token is written in the Header.
        
        Returns:
            - True/False
        '''

        return self.role == Role.ADMIN


    @classmethod
    def from_query_result(cls, id, username, password, role):
        ''' When User Model is shown in the response.
        
        Returns:
            - id, username, role
        '''
        
        return cls(
            id=id,
            username=username,
            password=password,
            role=role
            )

    @classmethod
    def from_query_result_no_password(cls, id, username, password, role):
        ''' When User Model is shown in the response.
        
        Returns:
            - id, username, role
        '''
        
        return cls(
            id=id,
            username=username,
            password='',
            role=role
            )
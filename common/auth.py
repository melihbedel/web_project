from fastapi import HTTPException
from data.models.user import User
from data.database import read_query
import jwt


_JWT_SECRET = ';a,jhsd1jahsd1kjhas1kjdh'


def get_user_or_raise_401(token: str) -> User:
    ''' Authenticates the given token in Header and finds the whole information of the user through its username:
    
    Args:
        - token (str): text with indents
    '''

    try:
        payload = is_authenticated(token)
        return find_by_username(payload['username'])
    except:
        raise HTTPException(status_code=401)


def compare_token(token: str) -> User:
    ''' Drags the id from the token so it can be compared.

    Args:
        - token (str): text with indents

    Returns:
        - id of the token
    '''

    try:
        payload = is_authenticated(token)
        payload = find_by_username(payload['username'])
        return payload.id
    except:
        raise HTTPException(status_code=401)


def find_by_username(username: str) -> User | None:
    ''' Drags the id from the token so it can be compared.

    Args:
        - token (str): text with indents

    Returns:
        - id of the token
    '''

    data = read_query(
        'SELECT id, username, password, role FROM users WHERE username = ?',
        (username,))

    return next((User.from_query_result(*row) for row in data), None)


def find_by_id(id: int) -> User | None:
    ''' Search through users.id the whole information about the account in the data.
     
    Args:
        - id: int 
        
    Returns:
        - all the necessary information about the user (id, username, hashed password, role and etc.)
    '''

    data = read_query(
        'SELECT id, username, password, role FROM users WHERE id = ?',
        (id,))

    return next((User.from_query_result(*row) for row in data), None)


def create_token(user: User) -> str:
    ''' Creates JWT token when user uses login request.
    
    Args:
        - user: id(int), username(str)
    
    Returns:
        - encoded JWT token
    '''

    payload = {
        "id": user.id,
        "username": user.username
    }
   
    return jwt.encode(payload, _JWT_SECRET, algorithm="HS256")


def is_authenticated(token: str) -> bool:
    ''' Decodes JWT token.
    
    Args:
        - encoded JWT token
    
    Returns:
        - user: id(int), username(str)
    '''

    return jwt.decode(token, _JWT_SECRET, algorithms=["HS256"])
from fastapi import APIRouter, Header, HTTPException
from common.auth import get_user_or_raise_401, create_token, find_by_id
from data.models.user import User, LoginData
from services import user_service, utils


users_router = APIRouter(prefix='/users', tags=['Users'])


@users_router.post('/register')
def register(data: LoginData):
    ''' Used for registering new users.
    
    Args:
        - LoginData(username, password(str))
    
    Returns:
        - Registered user as customer
    '''
    
    user = user_service.create(data.username, data.password)

    return user or HTTPException(status_code=400, detail=f'Username {data.username} is already taken.')


@users_router.post('/login')
def login(data: LoginData):
    ''' Used for logging in.

    Args:
        - LoginData(username, password(str))

    Returns:
        - JWT token
    '''

    user = user_service.try_login(data.username, data.password)

    if user:
        token = create_token(user)
        return {'token': token}
    else:
        raise HTTPException(status_code=400, detail='Invalid login data.')


@users_router.get('/info/all')
def all_users(x_token: str = Header(default=None)):
    ''' Used for admins to see a list with all users.
    
    Args:
        - JWT token
    
    Returns:
        - list of users(id, username, role)
    '''

    if x_token == None:
        raise HTTPException(status_code=401, detail='You must be logged in and be an admin to be able to view a list with users.')
    
    user = get_user_or_raise_401(x_token)
    
    if not User.is_admin(user):
        raise HTTPException(status_code=401, detail='Only admins can view a list with all users.')
    
    return user_service.find_all_users()


@users_router.get('/info/id/{id}')
def user_info(id: int, x_token: str = Header(default=None)):
    ''' Used for admins to see data information about a user.
    
    Args:
        - user.id: int(URL link)
        - JWT token
    
    Returns:
        - user(id, username, role)
    '''

    if x_token == None:
        raise HTTPException(status_code=401, detail='You must be logged in and be an admin to be able to review accounts.')
    
    user = get_user_or_raise_401(x_token)
    
    if not User.is_admin(user):
        raise HTTPException(status_code=401, detail='Only admins can review accounts.')
    
    if not utils.id_exists(id, 'users'):
        raise HTTPException(status_code=404, detail=f'User with id {id} does not exist.')
    
    return user_service.find_by_id_admin(id)


@users_router.get('/info/username/{username}')
def user_info(username: str, x_token: str = Header(default=None)):
    ''' Used for admins and customers to see data information about a user.
    
    Args:
        - user.username: str(URL link)
        - JWT token
    
    Returns:
        - user(id, username, role)
    '''

    if x_token == None:
        raise HTTPException(status_code=401, detail='You must be logged in and be an admin to be able to search accounts.')
    
    user = get_user_or_raise_401(x_token)

    if not utils.username_exists(username, 'users'):
        raise HTTPException(status_code=404, detail=f'User with username {username} does not exist.')
    
    if User.is_admin(user):
        return user_service.find_by_username_info(username)
    elif User.is_customer(user):
        return user_service.find_by_username_info(username)
    else:
        raise HTTPException(status_code=401, detail='Only logged in users and admins can search accounts.')


@users_router.put('/edit/{id}')
def edit_users_role(new_user: User, id: int, x_token: str = Header(default=None)):
    ''' Used for editing a user's role through user.id. Only admins can edit it.

    Args:
        - user.id: int(URL link)
        - JWT token
    
    Returns:
        - Edited user
    '''

    if x_token == None:
        raise HTTPException(status_code=401, detail='You must be logged in and be an admin to be able to edit users roles.')
    
    user = get_user_or_raise_401(x_token)
    
    if not User.is_admin(user):
        raise HTTPException(status_code=401, detail='Only admins can edit roles.')

    if not utils.id_exists(id, 'users'):
        raise HTTPException(status_code=404, detail=f'User with id {id} does not exist.')

    if new_user.role != 'admin' and new_user.role != 'customer':
        raise HTTPException(status_code=404, detail='Unknown role.')
    
    old_user = find_by_id(id)

    return user_service.edit_user(old_user, new_user)


@users_router.delete('/delete/{id}')
def delete_user(id: int, x_token: str = Header(default=None)):
    ''' Used for deleting a user through user.id. Only admins can delete it.

    Args:
        - user.id: int(URL link)
        - JWT token
    
    Returns:
        - Deleted user
    '''

    if x_token == None:
        raise HTTPException(status_code=401, detail='You must be logged in and be an admin to be able to delete a user.')    
    
    user = get_user_or_raise_401(x_token)

    if not utils.id_exists(id, 'users'):
        raise HTTPException(status_code=404, detail=f'User with id {id} does not exist.')

    if User.is_admin(user):
        user_service.delete_user(id)
    
    if User.is_customer(user):
        raise HTTPException(status_code=401, detail='You must be admin to be able to delete a user.')
        
    return {'User deleted.'}
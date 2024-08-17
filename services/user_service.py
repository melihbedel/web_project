from data.database import insert_query, update_query, read_query
from data.models.user import Role, User
from data.models.topic import Topic
from common.auth import find_by_username


def _hash_password(password: str):
    ''' Used to hash a password of a user before saving it in the database.'''
    from hashlib import sha256
    return sha256(password.encode('utf-8')).hexdigest()


def try_login(username: str, password: str) -> User | None:
    ''' Used to hash the login password and compare it with the existing password of the user in the database.'''

    user = find_by_username(username)

    password = _hash_password(password)
    return user if user and user.password == password else None


def create(username: str, password: str) -> User | None:
    ''' Used to save the already hashed password to the database.'''

    password = _hash_password(password)

    generated_id = insert_query(
        'INSERT INTO users(username, password, role) VALUES (?,?,?)',
        (username, password, Role.CUSTOMER))

    return User(id=generated_id, username=username, password='', role=Role.CUSTOMER)


def delete_user(id: int):
    ''' Used for deleting the user from the database.'''

    insert_query('''DELETE FROM users WHERE id = ?''',
                 (id,))
    

def edit_user(old_user: User, new_user: User):
    ''' Used for editing by an admin a role of a user in the database.'''
    
    edited_user = User(
        id=old_user.id,
        username=old_user.username,
        password=old_user.password,
        role=new_user.role
    )

    update_query('''UPDATE users SET role = ? WHERE id = ?''',
                (edited_user.role, edited_user.id))

    return {"User's role updated."}


def owns_topic(user: User, topic: Topic) -> bool:
    ''' Used to compares the topic.user_id with the user's token id.'''
    
    return topic.user_id == user.id


def find_all_users() -> User | None:
    ''' Search in the database and creates a list of all users. Only admins can view a list of all users.
     
    Returns:
        - a list of all users(id, username, role)
    '''

    data = read_query('SELECT id, username, password, role FROM users')

    result = (User.from_query_result_no_password(*row) for row in data)

    return result


def find_by_id_admin(id: int) -> User | None:
    ''' Search through users.id the whole information about the account in the data. Only admins can search for them.
     
    Args:
        - id: int 
        
    Returns:
        - all the necessary information about the user (id, username, hashed password, role and etc.)
    '''

    data = read_query(
        'SELECT id, username, password, role FROM users WHERE id = ?',
        (id,))

    return next((User.from_query_result_no_password(*row) for row in data), None)


def find_by_username_info(username: str) -> User | None:
    ''' Drags the username from the token so it can be compared and returns user.id

    Args:
        - username (str):

    Returns:
        - id of the user
    '''

    data = read_query(
        'SELECT id, username, password, role FROM users WHERE username = ?',
        (username,))

    return next((User.from_query_result_no_password(*row) for row in data), None)
from datetime import datetime
from fastapi import HTTPException
from data.database import read_query, insert_query, update_query
from data.models.topic import Topic
from services import reply_service


def all(search: str = None):
    ''' Used for getting all topics(private and non-private) from database. Used functions for admins requests.

    Returns:
        - List of all topics
    '''

    if search is None:
        data = read_query('''SELECT id, title, body, category_id, user_id, is_locked, is_private, best_reply_id, created_at FROM topics''') 
    else:
        data = read_query('''SELECT id, title, body, category_id, user_id, is_locked, is_private, best_reply_id, created_at 
                          FROM topics
                          WHERE title LIKE ?''', (f'%{search}%',))

    result = (Topic.from_query_result(*row) for row in data)

    return result 


def all_non_private(search: str = None):
    ''' Used for getting all topics(only non-private) from database. Used functions for customers requests.

    Returns:
        - List of all non-private topics
    '''

    if search is None:
        data = read_query('''SELECT id, title, body, category_id, user_id, is_locked, is_private, best_reply_id, created_at 
                          FROM topics
                          WHERE is_private = 0''')
    
    result = (Topic.from_query_result(*row) for row in data)

    return result 


def get_by_id(id, search):
    ''' Used for getting a single topic by topic.id.
    
    Returns:
        - topic
    '''

    data = read_query('SELECT id, title, body, category_id, user_id, is_locked, is_private, best_reply_id, created_at FROM topics WHERE id = ?', (id,))
    if not any(data):
        raise HTTPException(status_code=404)
    
    topic = next((Topic.from_query_result(*row, ) for row in data), None)

    if search is None:
        reply_ids = read_query('SELECT id FROM replies where topic_id = ?', (id,))
    else:
        reply_ids = read_query('SELECT id FROM replies WHERE topic_id = ? AND content LIKE ?', (id, f'%{search}%'))

    best_reply_id = read_query('SELECT best_reply_id FROM topics WHERE id = ?', (id,))
    if best_reply_id[0][0] is not None:
        topic.best_reply_id = reply_service.get_reply_by_id(best_reply_id[0][0])

    replies = [reply_service.get_reply_by_id(reply[0]) for reply in reply_ids]
    topic.replies = replies
    topic.created_at = topic.created_at.strftime("%Y-%m-%d %H:%M:%S")
    
    return topic


def sort(topics: list[Topic], *, attribute=None, reverse=False):
    ''' Used for sorting all topics. Can be sorted by: title, created_at, id. Can be sorted also in reverse.

    Returns:
        - sorted list of topics
    '''

    if attribute == 'title':
        sort_fn = lambda t: t.title
    elif attribute == 'created_at':
        sort_fn = lambda t: t.created_at
    else:
        sort_fn = lambda t: t.id
    return sorted(topics, key=sort_fn, reverse=reverse)


def create(topic: Topic, user_id: int, category_id: int):
    ''' Used for saving the created topic to the database.
    
    Returns:
        - topic
    '''

    DATETIME_NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    topic.category_id = category_id
    topic.user_id = user_id
    generated_id = insert_query(
        'INSERT INTO topics(title, body, category_id, user_id, is_locked, is_private, best_reply_id, created_at) VALUES(?,?,?,?,?,?,?,?)',
        (topic.title, topic.body, topic.category_id, topic.user_id, topic.is_locked, topic.is_private, topic.best_reply_id, DATETIME_NOW))

    topic.id = generated_id
    topic.created_at = DATETIME_NOW
    
    return topic


def delete_topic(id: int):
    ''' Used for deleting the topic and all replies in it from the database.'''

    reply_ids = read_query('SELECT id FROM replies WHERE topic_id = ?', (id,))

    for reply_id in reply_ids:
        reply_service.delete_reply(reply_id[0])

    insert_query('''DELETE FROM topics WHERE id = ?''',
                 (id,))


def edit_topic(old_topic: Topic, new_topic: Topic):
    ''' Used for editing title, body of a topic in the database.'''
    
    edited_topic = Topic(
        id=old_topic.id,
        title=new_topic.title,
        body=new_topic.body,
        category_id=old_topic.category_id,
        user_id=old_topic.user_id,
        is_locked=old_topic.is_locked,
        is_private=old_topic.is_private,
        created_at=old_topic.created_at
    )

    update_query('''UPDATE topics SET title = ?, body = ? WHERE id = ?''',
                (edited_topic.title, edited_topic.body, edited_topic.id))

    return edited_topic


def edit_topic_admin(old_topic: Topic, new_topic: Topic):
    ''' Used for editing title, body, category_id, is_locked, is_private of a topic in the database.'''

    edited_topic = Topic(
        id=old_topic.id,
        title=new_topic.title,
        body=new_topic.body,
        category_id=new_topic.category_id,
        user_id=old_topic.user_id,
        is_locked=new_topic.is_locked,
        is_private=new_topic.is_private,
        created_at=old_topic.created_at
    )

    update_query('''UPDATE topics SET title = ?, body = ?, category_id = ?, is_locked = ?, is_private = ? WHERE id = ?''',
                (edited_topic.title, edited_topic.body, edited_topic.category_id, edited_topic.is_locked, edited_topic.is_private, edited_topic.id))

    return edited_topic


def topic_locked(topic_id: int):
    locked = read_query('SELECT is_locked FROM topics WHERE id = ?', (topic_id,))[0][0]

    if locked:
        return True
    return False
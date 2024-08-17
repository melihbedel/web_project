from fastapi import HTTPException
from data.database import read_query, insert_query, update_query
from data.models.topic import Topic
from data.models.reply import Reply
from datetime import datetime


def get_reply_by_id(reply_id: int):
    ''' Used for getting a reply by reply.id from a topic from the database.'''

    reply_data = read_query('SELECT id, creation_date, content, topic_id, user_id FROM replies where id = ?', (reply_id,))

    upvotes = len(read_query('SELECT * FROM votes WHERE reply_id = ? AND vote = ?', (reply_id, 1)))
    downvotes = len(read_query('SELECT * FROM votes WHERE reply_id = ? AND vote = ?', (reply_id, 0)))

    reply_with_vote = reply_data[0] + (upvotes, downvotes)

    reply = Reply.from_query_result(*reply_with_vote)
    reply.creation_date = reply.creation_date.strftime("%Y-%m-%d %H:%M:%S")

    return reply


def get_topic_reply(topic_id, reply_id):
    ''' Used for getting a topic and a specific reply by topic.id and reply.id from the database.'''

    data = read_query('SELECT id, title, body, category_id, user_id, is_locked, is_private, best_reply_id, created_at FROM topics WHERE id = ?', (topic_id,))
    if not any(data):
        raise HTTPException(status_code=404)
    
    topic = next((Topic.from_query_result(*row, ) for row in data), None)

    reply_ids = read_query('SELECT id FROM replies WHERE topic_id = ? AND id = ?', (topic_id, reply_id))
    if not any(reply_ids):
        raise HTTPException(status_code=404)

    replies = [get_reply_by_id(reply[0]) for reply in reply_ids]
    topic.replies = replies
    
    return topic


def sort(replies: list[Reply], *, attribute=None, reverse=False):
    ''' Used for sorting all replies in a topic. Can be sorted by: creation_date, upvotes, downvotes, id. Can be sorted also in reverse.

    Returns:
        - sorted list of replies
    '''

    if attribute == 'creation_date':
        sort_fn = lambda r: r.creation_date
    elif attribute == 'upvotes':
        sort_fn = lambda r: r.upvotes
    elif attribute == 'downvotes':
        sort_fn = lambda r: r.downvotes
    else:
        sort_fn = lambda r: r.id

    return sorted(replies, key=sort_fn, reverse=reverse)


def create(reply: Reply, topic_id: int, user_id: int):
    ''' Used for saving the created reply to the database.
    
    Returns:
        - reply
    '''
    
    DATETIME_NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reply.topic_id = topic_id
    reply.user_id = user_id

    generated_id = insert_query('INSERT INTO replies (creation_date, content, topic_id, user_id) VALUES (?,?,?,?)', (DATETIME_NOW, reply.content, topic_id, user_id))
    
    reply.creation_date = DATETIME_NOW
    reply.id = generated_id

    return reply


def delete_reply(id: int):
    ''' Used for deleting a reply by reply.id in a topic in the database.'''

    insert_query('DELETE FROM votes WHERE reply_id = ?', (id,))
    insert_query('DELETE FROM replies WHERE id = ?', (id,))


def edit_reply(old_reply: Reply, new_reply: Reply):
    ''' Used for editing a reply by reply.id in a topic in the database.'''
    
    edited_reply = Reply(
        id = old_reply.id,
        creation_date=old_reply.creation_date,
        content=new_reply.content,
        topic_id=old_reply.topic_id,
        user_id=old_reply.user_id
    )

    update_query('''UPDATE replies SET content = ? WHERE id = ?''', (edited_reply.content, edited_reply.id))

    return edited_reply


def assign_best_reply(topic_id: int, reply_id: int):
    ''' Used for assigning a best reply in a topic by topic.id reply_id in the database.'''

    update_query('UPDATE topics SET best_reply_id = ? WHERE id = ?', (reply_id, topic_id))


def remove_best_reply(topic_id: int):
    ''' Used for removing a best reply in a topic by topic.id in the database.'''

    update_query('UPDATE topics SET best_reply_id = NULL WHERE id = ?', (topic_id,))
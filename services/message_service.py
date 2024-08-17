from datetime import datetime
from fastapi import APIRouter, HTTPException
from data.database import insert_query, read_query, read_query_additional, update_query
from data.models.message import Message, MessageResponseModel


def all():
    ''' Used for getting all messages from database.

    Returns:
        - List of all messages
    '''

    messages = read_query_additional('''SELECT * FROM messages''')

    if messages:
        return (MessageResponseModel.from_query_result(*msg) for msg in messages)
    else:
        return HTTPException(status_code=404, content='No messages found.')
    

def get_conversation(sender_id, receiver_id):
    ''' Used for getting the whole conversation between two users from the database.'''

    messages = read_query('''SELECT * FROM messages WHERE (sender_id = ? AND receiver_id = ?)
                           OR (sender_id = ? AND receiver_id = ?)
                           ORDER BY timestamp ASC''', (sender_id, receiver_id, receiver_id, sender_id))
    
    if messages:
        return [MessageResponseModel.from_query_result(*msg) for msg in messages]
    

def get_by_id(id: int):
    ''' Used for getting a message by message.id from a conversation between two users from the database.'''

    message = read_query_additional('''SELECT * from messages WHERE id = ?''', (id,))

    if message:
        return MessageResponseModel.from_query_result(*message)
    else:
        return HTTPException(status_code=404, content=f'Message with ID:{id} not found.')
    

def get_conversations_list(sender_id):
    ''' Used for getting all conversations of the user from the database.'''

    conversations = read_query(
        '''SELECT DISTINCT users.username 
           FROM messages
           JOIN users ON messages.receiver_id = users.id
           WHERE sender_id = ?''', 
        (sender_id,))
    
    return conversations


def send_message(
        message: Message,
        sender_id: int,
        receiver_id: int):
    ''' Used for saving a new message in a conversation in the database.'''

    DATETIME_NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    generated_id = insert_query('''INSERT INTO messages(content, timestamp, sender_id, receiver_id) VALUES (?, ?, ?, ?)''',
                                (message.content, DATETIME_NOW, sender_id, receiver_id))
    
    message.id = generated_id
    message.timestamp = DATETIME_NOW

    return message


def delete_message(id: int):
    ''' Used for deleting a message by message.id in a conversation in the database.'''

    insert_query('''DELETE FROM messages WHERE id = ?''',
                 (id,))


def edit_message(old_message: Message, new_message: Message):
    ''' Used for editing a message by message.id in a conversation in the database.'''
    
    edited_message = Message(
        id = old_message.id,
        content= new_message.content,
        timestamp= old_message.timestamp,
        sender_id= old_message.sender_id,
        receiver_id=old_message.receiver_id
    )

    update_query('''UPDATE messages SET content = ? WHERE id= ?''', (edited_message.content, edited_message.id))

    return edited_message
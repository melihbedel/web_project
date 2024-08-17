from fastapi import APIRouter, HTTPException, Header
from services import message_service
from data.models.message import Message, CreateMessageModel
from services.utils import id_exists
from common.auth import get_user_or_raise_401


messages_router = APIRouter(prefix='/messages', tags=['Messages'])


@messages_router.get('/conversation/{sender_id}/to/{receiver_id}',status_code=200)
def view_conversation(sender_id: int, receiver_id, x_token: str = Header(default=None)):
    ''' Used for viewing a conversation. The conversation can be viewed by the sender and also by the receiver.
    
    Args:
        - sender_id: int(URL link)
        - receiver_id: int(URL link)
        - JWT token(Header)
    
    Returns:
        - The whole conversation between the two user id's
    '''

    if x_token == None:
        raise HTTPException(status_code=401, detail='You need to log-in to send a message.')    
    if sender_id != get_user_or_raise_401(x_token).id:
        raise HTTPException(status_code=401, detail='Viewing conversations of other accounts is not possible.')

    if not id_exists(receiver_id, 'users'):
        raise HTTPException(status_code=404, detail=f'Receiver with ID: {receiver_id} does not exist.')
    if not id_exists(sender_id, 'users'):
        raise HTTPException(status_code=404, detail=f'Sender with ID: {sender_id} does not exist.')
    if sender_id == receiver_id:
        raise HTTPException(status_code=400, detail='Conversation does not exist.')
    
    all_messages = message_service.get_conversation(sender_id, receiver_id)

    return all_messages


@messages_router.get('/{sender_id}/my_conversations', status_code=200)
def get_conversations(sender_id: int, x_token: str = Header(default=None)):
    ''' Used for viewing all conversations of the user.
    
    Args:
        - sender_id: int(URL link)
        - JWT token(Header)
    
    Returns:
        - A list of all conversations
    '''
    
    if x_token == None:
        raise HTTPException(status_code=401, detail='You need to log-in to view conversations list.')
    if not id_exists(sender_id, 'users'):
        raise HTTPException(status_code=404, detail=f'Sender with ID: {sender_id} does not exist.')
    if sender_id != get_user_or_raise_401(x_token).id:
        raise HTTPException(status_code=401, detail="You can not view other people's conversations.")
    
    conversations = message_service.get_conversations_list(sender_id)

    return {'You have conversations with:': (user[0] for user in conversations)}


@messages_router.post('/{sender_id}/to/{receiver_id}', status_code=201)
def send_new_message(message: CreateMessageModel, sender_id: int, receiver_id: int, x_token: str = Header(default=None)):
    ''' Used for sending a message to another user.
    
    Args:
        - CreateMessageModel(content(str), timestamp(datetime))
        - sender_id: int(URL link)
        - receiver_id: int(URL link)
        - JWT token(Header)
    
    Returns:
        - New Message
    '''

    if x_token == None:
        raise HTTPException(status_code=401, detail='You need to log-in to send a message.')    
    if sender_id != get_user_or_raise_401(x_token).id:
        raise HTTPException(status_code=401, detail='Sending message from wrong account is not possible.')
   
    if not id_exists(receiver_id, 'users'):
        raise HTTPException(status_code=404, detail=f'Receiver with ID: {receiver_id} does not exist.')
    if not id_exists(sender_id, 'users'):
        raise HTTPException(status_code=404, detail=f'Sender with ID: {sender_id} does not exist.')
    if sender_id == receiver_id:
        raise HTTPException(status_code=400, detail='You are trying to message yourself. Try a different receiver ID.')
    
    message_service.send_message(message, sender_id, receiver_id)

    return {'Message sent.'}


@messages_router.put('/edit/{id}')
def edit_message_by_id(new_message: Message, id: int, x_token: str = Header(default=None)):
    ''' Used for editing a message through id(of the message). Only the sender of the message can edit it.
    
    Args:
        - Message Model(content(str))
        - id(of the message): int(URL link)
        - JWT token(Header)
    
    Returns:
        - Updated message
    '''

    if x_token == None:
        raise HTTPException(status_code=401, detail='You need to log-in to edit a message.')    
    if message_service.get_by_id(id).sender_id != get_user_or_raise_401(x_token).id:
        raise HTTPException(status_code=401, detail='Editing other account message is not possible.')
    
    if not id_exists(id, 'messages'):
        raise HTTPException(status_code=404, detail=f'Message with id {id} does not exist.')
    old_message = message_service.get_by_id(id)

    message_service.edit_message(old_message, new_message)

    return {'Message updated.'}


@messages_router.delete('/delete/{id}')
def delete_message(id: int, x_token: str = Header(default=None)):
    ''' Used for deleting a message through id(of the message). Only the sender of the message can delete it.
    
    Args:
        - id(of the message): int(URL link)
        - JWT token(Header)
    
    Returns:
        - Deleted message
    '''
    
    if not id_exists(id, 'messages'):
        raise HTTPException(status_code=404, detail=f'Message with id {id} does not exist.')
    if x_token == None:
        raise HTTPException(status_code=401, detail='You need to log-in to delete a message.')    
    if message_service.get_by_id(id).sender_id != get_user_or_raise_401(x_token).id:
        raise HTTPException(status_code=401, detail='Deleting messages from wrong account is not possible.')
    
    message_service.delete_message(id)

    return {'Message deleted.'}
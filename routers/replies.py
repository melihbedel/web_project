from fastapi import APIRouter, HTTPException, Header
from common.auth import get_user_or_raise_401
from data.models.user import User
from data.models.reply import Reply
from services import reply_service
from data.models.reply import CreateReplyModel
from services.utils import id_exists


replies_router = APIRouter(prefix='/replies', tags=['Replies'])


@replies_router.get('/{id}', status_code=200)
def get_reply(id: int):
    ''' Used for viewing only the raw reply through id(of the reply).
    
    Args:
        - reply.id
    
    Returns:
        - raw reply
    '''

    if not id_exists(id, 'replies'):
        raise HTTPException(status_code=404, detail=f'Reply with id {id} does not exist.')
    
    result = reply_service.get_reply_by_id(id)

    return result


@replies_router.put('/edit/{id}')
def edit_reply_by_id(new_reply: Reply, id: int, x_token: str = Header(default=None)):
    ''' Used for editing a reply through reply.id. Only the owner of the reply and admins can edit it.
    
    Args:
        - Reply(content(str))
        - reply.id: int(URL link)
        - JWT token(Header)
    
    Returns:
        - Edited reply
    '''

    if x_token == None:
        raise HTTPException(status_code=401, detail='You need to be logged in to edit a reply.')    
    
    if not id_exists(id, 'replies'):
        raise HTTPException(status_code=404, detail=f'Reply with id {id} does not exist.')
    
    user = get_user_or_raise_401(x_token)
    
    old_reply = reply_service.get_reply_by_id(id)

    if User.is_admin(user):
        reply_service.edit_reply(old_reply, new_reply)

    if User.is_customer(user):
        if user.id == old_reply.user_id:
            reply_service.edit_reply(old_reply, new_reply)
        else:
            raise HTTPException(status_code=401, detail='You must be the owner of the reply to be able to edit.')

    return {'Reply updated.'}


@replies_router.delete('/delete/{id}')
def delete_reply(id: int, x_token: str = Header(default=None)):
    ''' Used for deleting a reply through reply.id. Only the owner of the reply and admins can delete it.
    
    Args:
        - reply.id: int(URL link)
        - JWT token(Header)
    
    Returns:
        - Deleted reply
    '''

    if x_token == None:
        raise HTTPException(status_code=401, detail='You need to be logged in to delete a reply.')
    
    if not id_exists(id, 'replies'):
        raise HTTPException(status_code=404, detail=f'Reply with id {id} does not exist.')
    
    user = get_user_or_raise_401(x_token)

    reply = reply_service.get_reply_by_id(id)

    if User.is_admin(user):
        reply_service.delete_reply(id)
    
    if User.is_customer(user):
        if user.id == reply.user_id:
            reply_service.delete_reply(id)
        else:
            raise HTTPException(status_code=401, detail='You must be the owner of the reply.')
        
    return {'Reply deleted.'}

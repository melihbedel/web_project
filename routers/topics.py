from fastapi import APIRouter, Query, Header, HTTPException
from data.models.reply import CreateReplyModel
from data.models.topic import Topic, CreateTopicModel
from data.models.user import User
from services.utils import id_exists
from services import topic_service
from services import reply_service
from services import vote_service
from services.utils import paginate, get_page
from common.auth import get_user_or_raise_401


topics_router = APIRouter(prefix='/topics', tags=['Topics'])


@topics_router.get('/', status_code=200)
def get_all_topics(
    sort: str | None = None, 
    sort_by: str | None = None, 
    search: str | None = None,
    page: int | None = None,
    pagination: int | None = None,
    x_token: str = Header(default=None)
):
    ''' Used for viewing all topics in the forum.
    
    Returns:
        - if user.role is 'admin': all topics(private and non-private)
        - if user.role is 'customer: topics(non-private)
    '''

    if x_token != None:
        user = get_user_or_raise_401(x_token)
    
        if User.is_customer(user):
            topics = topic_service.all_non_private(search)
        elif User.is_admin(user):
            topics = topic_service.all(search)
    else:
        topics = topic_service.all_non_private(search)
    
    if sort and (sort == 'asc' or sort == 'desc'):
        topics = topic_service.sort(topics, reverse=sort == 'desc', attribute=sort_by)
    if pagination:
        topics = paginate(topics, pagination)
    if page:
        topics = get_page(topics, page)  

    return topics
        

@topics_router.get('/{id}')
def get_topic_by_id(id: int, x_token: str = Header(default=None),
    sort_replies: str | None = Query(None, alias="sort"), 
    sort_replies_by: str | None = Query(None, alias="sort_by"), 
    search_replies: str | None = Query(None, alias="search"),
    page: int | None = None,
    pagination: int | None = None):
    ''' Used for viewing a topic through topic.id.
    
    Args:
        - token.id: int(URL link)
    
    Returns:
        - if user.role is 'admin': topic(private and non-private)
        - if user.role is 'customer: topic(non-private)
    '''

    if not id_exists(id, 'topics'):
        raise HTTPException(status_code=404, detail=f'Topic with id: {id} does not exist.')
    
    topic = topic_service.get_by_id(id, search_replies)

    if topic.is_private == True:
        if x_token != None:
            user = get_user_or_raise_401(x_token)
    
            if User.is_customer(user):
                raise HTTPException(status_code=400, detail=f'The topic with id {id} is private.')
            elif User.is_admin(user):
                topic = topic_service.get_by_id(id, search_replies)
            
    if sort_replies and (sort_replies == 'asc' or sort_replies == 'desc'):
        topic.replies = reply_service.sort(topic.replies, attribute=sort_replies_by, reverse=sort_replies == 'desc')
    if pagination:
        topic.replies = paginate(topic.replies, pagination)
    if page:
        topic.replies = get_page(topic.replies, page)  

    return topic


@topics_router.get('/{id}/{reply_id}')
def get_reply_with_topic(id: int, reply_id: int, x_token: str = Header(default=None)):
    ''' Used for viewing a reply with its topic through topic.id and reply_id.
    
    Args:
        - topic.id: int(URL link)
        - reply_id: int(URL link)
        - JWT token(Header)
    
    Returns:
        - if user.role is 'admin': topic(private and non-private) with a reply
        - if user.role is 'customer: topic(non-private) with a reply
    '''

    if not id_exists(id, 'topics'):
        raise HTTPException(status_code=404, detail=f'Topic with id: {id} does not exist.')
    
    if not id_exists(reply_id, 'replies'):
        raise HTTPException(status_code=404, detail=f'Reply with id: {reply_id} does not exist.')
    
    topic = reply_service.get_topic_reply(id, reply_id)

    if topic.is_private == True:
        if x_token != None:
            user = get_user_or_raise_401(x_token)
    
            if User.is_customer(user):
                raise HTTPException(status_code=400, detail=f'The topic with id {id} is private.')
            elif User.is_admin(user):
                topic = reply_service.get_topic_reply(id, reply_id)
          
    return topic


@topics_router.post('/categories/{id}')
def create_topic(topic: CreateTopicModel, id: int, x_token: str = Header(default=None)):
    ''' Used for creating a topic in a category. Only admins and customers can create topics. Admins can create private topics.

    Args:
        - CreateTopicModel(title(str), body(str))
        - category.id: int(URL link)
        - JWT token
    
    Returns:
        - Created topic
    '''

    if not id_exists(id, 'categories'):
        raise HTTPException(status_code=404, detail=f'Category with id {id} does not exist.')
    
    if x_token == None:
        raise HTTPException(status_code=401, detail='You must be logged in to be able to create a new topic.')
    
    user = get_user_or_raise_401(x_token)
    user_id = user.id
    category_id = id

    if User.is_admin(user):
        return topic_service.create(topic, user_id, category_id)
    elif User.is_customer(user):
        return topic_service.create(topic, user_id, category_id)
    else:
        raise HTTPException(status_code=401, detail='You must be logged in to be able to create a new topic.')


@topics_router.post('/{id}')
def post_reply(reply: CreateReplyModel, id: int, x_token: str = Header(default=None)):
    ''' Used for creating a reply in a topic.

    Args:
        - CreateReplyModel(content(str))
        - topic.id: int(URL link)
        - JWT token
    
    Returns:
        - Created reply
    '''
    
    if not id_exists(id, 'topics'):
        raise HTTPException(status_code=404, detail=f'Topic with id: {id} does not exist.')
    
    if x_token == None:
        raise HTTPException(status_code=401, detail='You must be logged in to be able to create a new reply.')
    
    if topic_service.topic_locked(id):
        raise HTTPException(status_code=403, detail='You cannot reply to a locked topic')
    
    user = get_user_or_raise_401(x_token)
    user_id = user.id
    topic_id = id

    if User.is_admin(user):
        return reply_service.create(reply, topic_id, user_id)
    elif User.is_customer(user):
        return reply_service.create(reply, topic_id, user_id)
    else:
        raise HTTPException(status_code=401, detail='You must be logged in to be able to create a new reply.')


@topics_router.post('/{id}/{reply_id}')
def reply_interact(id: int, reply_id: int, vote: str = Query(None, alias="vote"), best = Query(None, alias="best"), x_token: str = Header(default=None)):
    ''' User for giving a vote. Vote can be: upvote or downvote. It is used also for choosing a best reply in a topic by the topic's owner. Vote and best reply can be used together.
    
    Args:
        - topic.id: int(URL link)
        - reply_id: int(URL link)
        - vote: str(URL link) looks like: http://127.0.0.1:8000/topics/{topic_id}/{reply_id}?vote=
        - best: str(URL link) looks like: http://127.0.0.1:8000/topics/{topic_id}/{reply_id}?best=
        - JWT token
    
    Returns:
        - if vote: reply
        - if best: topic and a reply
    '''

    if x_token == None:
        raise HTTPException(status_code=401, detail='You must be logged in to be able to interact with replies.')
    
    user = get_user_or_raise_401(x_token)
    user_id = user.id

    if not id_exists(id, 'topics'):
        raise HTTPException(status_code=404, detail=f'Topic with id: {id} does not exist.')
    
    if not id_exists(reply_id, 'replies'):
        raise HTTPException(status_code=404, detail=f'Reply with id: {id} does not exist.')
    
    if not vote and not best:
        raise HTTPException(status_code=400, detail='Please vote or choose best reply.')

    if vote:
        if vote != 'upvote' and vote != 'downvote' and vote != 'clear':
            raise HTTPException(status_code=400, detail='Vote should be upvote, downvote or clear.')
        elif vote == 'clear':
            vote_service.delete_vote(reply_id, user_id)
            return reply_service.get_reply_by_id(reply_id)    
        elif vote_service.already_voted(reply_id, user_id, vote) == True:
            raise HTTPException(status_code=403, detail='You cannot vote twice on a reply.')
        elif vote_service.different_vote(reply_id, user_id, vote) == True:
            if vote == 'upvote' or vote == 'downvote':
                vote_service.update_vote(reply_id, user_id, vote)
                return reply_service.get_reply_by_id(reply_id)
        elif vote == 'upvote':
            vote_service.upvote(reply_id, user_id)
        else:
            vote_service.downvote(reply_id, user_id)
        return reply_service.get_reply_by_id(reply_id)

    topic = get_topic_by_id(id)
    if best:
        if user_id != topic.user_id:
            raise HTTPException(status_code=401, detail='You must be the owner of the topic to be able to edit best reply.')
        if best != 'assign' and best != 'remove':
            raise HTTPException(status_code=400, detail='Choose assign or remove.')       
        if best == 'assign':
            reply_service.assign_best_reply(id, reply_id)
            return get_topic_by_id(id)
        if best == 'remove':
            reply_service.remove_best_reply(id)
            return get_topic_by_id(id)


@topics_router.put('/edit/{id}')
def edit_topic_by_id(new_topic: Topic, id: int, x_token: str = Header(default=None)):
    ''' Used for editing a topic through topic.id. Only admins and owner of the topic can edit it.

    Args:
        - Topic(title(str), body(str))
        - topic.id: int(URL link)
        - JWT token
    
    Returns:
        - Edited topic
    '''

    if x_token == None:
        raise HTTPException(status_code=401, detail='You need to be logged in to edit a topic.')    
    
    if not id_exists(id, 'topics'):
        raise HTTPException(status_code=404, detail=f'Topic with id {id} does not exist.')
    
    user = get_user_or_raise_401(x_token)
    
    old_topic = get_topic_by_id(id)

    if User.is_admin(user):
        topic_service.edit_topic_admin(old_topic, new_topic)

    if User.is_customer(user):
        if user.id == old_topic.user_id:
            topic_service.edit_topic(old_topic, new_topic)
        else:
            raise HTTPException(status_code=401, detail='You must be the owner of the topic to be able to edit.')

    return {'Topic updated.'}


@topics_router.delete('/delete/{id}')
def delete_topic(id: int, x_token: str = Header(default=None)):
    ''' Used for deleting a topic through topic.id. Only admins and owner of the topic can delete it.

    Args:
        - topic.id: int(URL link)
        - JWT token
    
    Returns:
        - Deleted topic
    '''

    if x_token == None:
        raise HTTPException(status_code=401, detail='You need to be logged in to delete a topic.')
    
    if not id_exists(id, 'topics'):
        raise HTTPException(status_code=404, detail=f'Topic with id {id} does not exist.')
    
    user = get_user_or_raise_401(x_token)

    topic = get_topic_by_id(id)

    if User.is_admin(user):
        topic_service.delete_topic(id)
    
    if User.is_customer(user):
        if user.id == topic.user_id:
            topic_service.delete_topic(id)
        else:
            raise HTTPException(status_code=401, detail='You must be the owner of the topic.')
        
    return {'Topic deleted.'}

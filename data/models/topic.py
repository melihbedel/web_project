from pydantic import BaseModel, constr
from data.models.reply import Reply
from datetime import datetime


class Topic(BaseModel):
    id: int | None = None
    title: constr(min_length=3, max_length=40)
    body: constr(min_length=10, max_length=300)
    category_id: int
    user_id: int | None = None
    is_locked: bool | None = 0
    is_private: bool | None = 0
    best_reply_id: int | None = None
    replies: list[Reply] = []
    created_at: datetime | None = None
    

    @classmethod
    def from_query_result(cls, id, title, body, category_id, user_id, is_locked, is_private, best_reply_id, created_at):
        ''' When Reply Model is shown in the response.
        
        Returns:
            - id, title, body, category_id, user_id, is_locked, is_private, best_reply_id, created_at
        '''
        
        return cls(
            id=id,
            title=title,
            body=body,
            category_id=category_id,
            user_id=user_id,
            is_locked=is_locked,
            is_private=is_private,
            best_reply_id=best_reply_id,
            created_at=created_at
        )
    

class CreateTopicModel(BaseModel):
    id: int | None = None
    title: constr(min_length=3, max_length=40)
    body: constr(min_length=10, max_length=300)
    category_id: int | None = None
    user_id: int | None = None
    is_locked: bool | None = 0
    is_private: bool | None = 0
    best_reply_id: int | None = None
    created_at: datetime | None = None

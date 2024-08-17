from pydantic import BaseModel, constr
from datetime import datetime


class Reply(BaseModel):
    id: int | None = None
    creation_date: datetime | None = None
    content: constr(min_length=2, max_length=250)
    topic_id: int | None = None
    user_id: int | None = None
    upvotes: int | None = 0
    downvotes: int | None = 0


    @classmethod
    def from_query_result(cls, id, creation_date, content, topic_id, user_id, upvotes, downvotes):
        ''' When Reply Model is shown in the response.
        
        Returns:
            - id, creation_date, content, topic_id, user_id, upvotes, downvotes
        '''
        
        return cls(
                    id = id,
                    creation_date=creation_date,
                    content=content,
                    topic_id=topic_id,
                    user_id=user_id,
                    upvotes=upvotes,
                    downvotes=downvotes
        )


class CreateReplyModel(BaseModel):
    id: int | None = None
    creation_date: datetime | None = None
    content: constr(min_length=2, max_length=250)
    topic_id: int | None = None
    user_id: int | None = None
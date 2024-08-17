from pydantic import BaseModel, constr
from data.models.topic import Topic
from datetime import datetime


class Category(BaseModel):
    id: int | None = None
    name: constr(min_length=3, max_length=30)
    description: constr(min_length=3, max_length=50)
    is_locked: bool | None = 0
    is_private: bool | None = 0
    topics: list[Topic] = []
    created_at: datetime | None = None
    
    
    @classmethod
    def from_query_result(cls, id, name, description, is_locked, is_private, created_at):
        ''' When Category model is shown in the response.
        
        Returns:
            - id, name, description, is_locked, is private, created_at
        '''
        
        return cls(
            id=id,
            name=name,
            description=description,
            is_locked=is_locked,
            is_private=is_private,
            created_at=created_at
            )


class CreateCategoryModel(BaseModel):
    id: int | None = None
    name: constr(min_length=3, max_length=50)
    description: constr(min_length=3, max_length=50)
    is_locked: bool | None = 0
    is_private: bool | None = 0
    created_at: datetime | None = None
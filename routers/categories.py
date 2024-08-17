from fastapi import APIRouter, Query, Header, HTTPException
from data.models.category import Category, CreateCategoryModel
from services import category_service
from services import topic_service
from services.utils import id_exists
from common.auth import get_user_or_raise_401
from data.models.user import User
from services.utils import paginate, get_page


categories_router = APIRouter(prefix='/categories', tags=['Categories'])


@categories_router.get('/')
def get_categories(
    sort_cat: str | None = Query(None, alias="sort"), 
    sort_cat_by: str | None = Query(None, alias="sort_by"), 
    search_cat: str | None = Query(None, alias="search"),
    page: int | None = None,
    pagination: int | None = None,
    x_token: str = Header(default=None)
):
    ''' Finds all categories in the forum.
    
    Returns:
        - if user.role is 'admin': all categories(private and non-private)
        - if user.role is 'customer: categories(non-private)
    '''
    
    all_categories = category_service.all(search_cat)

    if x_token != None:
        user = get_user_or_raise_401(x_token)
    
        if User.is_customer(user):
            all_categories = category_service.all_non_private(search_cat)
        elif User.is_admin(user):
            all_categories = category_service.all(search_cat)
    else:
        all_categories = category_service.all_non_private(search_cat)


    if sort_cat and (sort_cat == 'asc' or sort_cat == 'desc'):
        all_categories = category_service.sort(all_categories, reverse=sort_cat == 'desc', attribute=sort_cat_by)
    if pagination:
        all_categories = paginate(all_categories, pagination)
    if page:
        all_categories = get_page(all_categories, page)

    return all_categories if all_categories else HTTPException(status_code=404, detail='There are no categories.')


@categories_router.get('/{id}')
def get_category_by_id(id: int,
    sort_topics: str | None = Query(None, alias="sort"),
    sort_topics_by: str | None = Query(None, alias="sort_by"),
    search_topics: str | None = Query(None, alias="search"),
    page: int | None = None,
    pagination: int | None = None,
    x_token: str = Header(default=None)
):
    ''' Finds the category through id.
    
    Returns:
        - if user.role is 'admin': category(private and non-private)
        - if user.role is 'customer: category(non-private)
    '''
    
    if not id_exists(id, 'categories'):
        raise HTTPException(status_code=404, detail=f'Category with id: {id} does not exist.')

    category = category_service.get_by_id(id, search_topics)
    
    if category.is_private == True:
        if x_token != None:
            user = get_user_or_raise_401(x_token)
    
            if User.is_customer(user):
                raise HTTPException(status_code=400, detail=f'The category with id {id} is private.')
            elif User.is_admin(user):
                category = category_service.get_by_id(id, search_topics)

    if sort_topics and (sort_topics == 'asc' or sort_topics == 'desc'):
        category = topic_service.sort(category.topics, reverse=sort_topics == 'desc', attribute=sort_topics_by)
    if pagination:
        category.topics = paginate(category.topics, pagination)
    if page:
        category.topics = get_page(category.topics, page)  

    return category 
    

@categories_router.post('/')
def create_category(category: CreateCategoryModel, x_token: str = Header(default=None)):
    '''Creates a category. Only an admin is allowed to create categories.

    Args:
        - CreateCategoryModel(name, description, is_locked(None), is_private(None), created_at(datetime))
        - JWT token(Header)

    Returns:
        - New Category created
    '''
    
    if x_token == None:
        raise HTTPException(status_code=401, detail='You must be logged in and be an admin to be able to create a new category.')
    
    user = get_user_or_raise_401(x_token)
    
    if not User.is_admin(user):
        raise HTTPException(status_code=401, detail='Only admins can create new categories.')

    return {'Category created:'}, category_service.create(category)


@categories_router.put('/edit/{id}')
def edit_category_by_id(new_category: Category, id: int, x_token: str = Header(default=None)):
    '''Used for editing a category through id. Only an admin is allowed to edit categories.

    Args:
        - Category(name, description, is_locked(None), is_private(None), created_at(datetime))
        - JWT token(Header)

    Returns:
        - Category updated
    '''

    if not id_exists(id, 'categories'):
        raise HTTPException(status_code=404, detail='Category does not exist.')
    
    if x_token == None:
        raise HTTPException(status_code=401, detail='You need to be logged in and be an admin to edit a category.')    

    user = get_user_or_raise_401(x_token)

    if not User.is_admin(user):
        raise HTTPException(status_code=401, detail='You must be an admin to edit a category.')
    
    old_category = category_service.get_by_id(id)

    return {'Category updated:'}, category_service.edit_category(old_category, new_category)


@categories_router.delete('/delete/{id}')
def delete_category(id: int, x_token: str = Header(default=None)):
    '''Used for deleting a category through id. Only an admin is allowed to delete categories.

    Args:
        - id of the category in the URL link
        - JWT token(Header)

    Returns:
        - Category deleted
    '''

    if not id_exists(id, 'categories'):
        raise HTTPException(status_code=404, detail='Category does not exist.')
    
    if x_token == None:
        raise HTTPException(status_code=401, detail='You need to be logged in and to be an admin to delete a message.')    
    
    user = get_user_or_raise_401(x_token)

    if not User.is_admin(user):
        raise HTTPException(status_code=401, detail='You must be an admin to delete a category.')
    
    category_service.delete_category(id)

    return {'Category deleted.'}
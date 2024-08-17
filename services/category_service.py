from datetime import datetime
from fastapi import APIRouter, Response, HTTPException
from data.database import insert_query, read_query, read_query_additional, update_query
from data.models.category import Category
from data.models.topic import Topic
from services import topic_service


def all(search: str = None):
    ''' Used for getting all categories(private and non-private) from database. Used functions for admins requests.

    Returns:
        - List of all categories
    '''

    if search is None:
        data = read_query('SELECT id, name, description, is_locked, is_private, created_at FROM categories')
    else:
        data = read_query('SELECT id, name, description, is_locked, is_private, created_at FROM categories WHERE name LIKE ?', (f'%{search}%',))

    result = (Category.from_query_result(*cat) for cat in data)

    return result if data else HTTPException(status_code=404, detail='There are no categories.')
    

def all_non_private(search: str = None):
    ''' Used for getting all categories(only non-private) from database. Used functions for customers requests.

    Returns:
        - List of all non-private categories
    '''

    if search is None:
        categories = read_query('''SELECT id, name, description, is_locked, is_private, created_at 
                                FROM categories 
                                WHERE is_private = 0''')
    else:
        categories = read_query('''
        SELECT id, name, description, is_locked, is_private, created_at
        FROM categories 
        WHERE is_private = 0 AND name LIKE ?''', (f'%{search}%',))  

    return (Category.from_query_result(*cat) for cat in categories) if categories else HTTPException(status_code=404, detail='There are no categories.')
    

def get_by_id(id: int, search: str = None):
    ''' Used for getting a single category by category.id.
    
    Args:
        - category.id: int(URL link)
    
    Returns:
        - category
    '''

    category = read_query_additional('SELECT id, name, description, is_locked, is_private, created_at FROM categories where id = ?',(id,)) 
                
    if category is None:
        raise HTTPException(status_code=404, detail=f'Category with id: {id} does not exist.')
    
    actual = Category.from_query_result(*category)

    if search is None:
        cat_topics = read_query('''SELECT * FROM topics where category_id = ?''', (id,))
    else:
        cat_topics = read_query('SELECT * FROM topics WHERE category_id = ? AND title LIKE ?', (id, f'%{search}%'))
    
    topics = [Topic.from_query_result(*topic) for topic in cat_topics]
    actual.topics = topics
    
    return actual
    

def sort(categories: list[Category], *, attribute=None, reverse=False):
    ''' Used for sorting all categories. Can be sorted by: name, created_at, id. Can be sorted also in reverse.

    Returns:
        - sorted list of categories
    '''

    if attribute == 'name':
        sort_fn = lambda c: c.name
    elif attribute == 'created_at':
        sort_fn = lambda c: c.created_at
    else:
        sort_fn = lambda c: c.id
    
    return sorted(categories, key=sort_fn, reverse=reverse)


def create(category: Category):
    ''' Used for saving the created category to the database.
    
    Returns:
        - category
    '''

    DATETIME_NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    generated_id = insert_query(
        'INSERT INTO categories(name, description, is_locked, is_private, created_at) values(?,?,?,?,?)',
        (category.name, category.description, category.is_locked, category.is_private, DATETIME_NOW))

    category.id = generated_id
    category.created_at = DATETIME_NOW
    

    return category


def delete_category(id: int):
    ''' Used for deleting the category and all topics in it from the database.'''
    
    topic_ids = read_query('SELECT id FROM topics WHERE category_id = ?', (id,))

    for topic_id in topic_ids:
        topic_service.delete_topic(topic_id[0])

    insert_query('''DELETE FROM categories WHERE id = ?''',
                 (id,))
    
    
def edit_category(old_category: Category, new_category: Category):
    ''' Used for editing name, description, is_locked, is_private of a category in the database.'''
    
    edited_category = Category(
        id=old_category.id,
        name=new_category.name,
        description=new_category.description,
        is_locked=new_category.is_locked,
        is_private=new_category.is_private,
        topics=old_category.topics,
        created_at=old_category.created_at
    )

    update_query('''UPDATE categories SET name = ?, description = ?, is_locked = ?, is_private = ?, created_at = ? WHERE id = ?''',
                (edited_category.name, edited_category.description, edited_category.is_locked, edited_category.is_private, edited_category.created_at, edited_category.id))

    if new_category.is_private == True:
        new_category.topics = update_query('''UPDATE topics SET is_private = 1 WHERE category_id = ?''', (old_category.id,))

    return edited_category
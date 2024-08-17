from fastapi import HTTPException
from data.database import read_query
from datetime import datetime


def name_exists(name: str, table_name: str) -> bool:
    ''' Used to check if the name exists in the table in the database.'''

    return any(
        read_query(
            f'SELECT name FROM {table_name} where name = ?',
            (name,)))


def username_exists(username: str, table_name: str) -> bool:
    ''' Used to check if the username exists in the table in the database.'''

    return any(
        read_query(
            f'SELECT username FROM {table_name} where username = ?',
            (username,)))


def id_exists(id: int, table_name: str) -> bool:
    ''' Used to check if the id exists in the table in the database.'''

    return any(
        read_query(
            f'SELECT id FROM {table_name} where id = ?',
            (id,)))


def get_page(data: list[dict], page: int=None):
    ''' Used for get a page of searched table in the database.'''

    result = []
    start_at = False
    for row in data:
        if page == 1:
            result.append(row)
            if isinstance(row, dict) and row['Page'] == page:  
                break  
        if isinstance(row, dict) and row['Page'] == page - 1:
            start_at = True
            continue
        if start_at:
            result.append(row)
        if isinstance(row, dict) and row['Page'] == page:  
            break  

    return result if result else HTTPException(
        status_code=404, content='Page does not exist.'
        )


def paginate(data: list, results_per_page: int=0):
    ''' Used to paginate the searched table in the database.'''

    if results_per_page == 0:
        return data
    result = []
    counter = 1
    for index, value in enumerate(data):
        next = (results_per_page * counter)
        if index == next:
            result.append({'Page': counter
            })
            next += results_per_page
            counter += 1
        result.append(value) 
    result.append({'Page': counter})   

    return result        

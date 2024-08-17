from data.database import insert_query, read_query, update_query


def upvote(reply_id, user_id):
    ''' Used to insert an upvote value into votes in the database.'''

    insert_query('INSERT INTO votes (reply_id, user_id, vote) VALUES (?,?,?)', (reply_id, user_id, 1))


def downvote(reply_id, user_id):
    ''' Used to insert a downvote value into votes in the database.'''

    insert_query('INSERT INTO votes (reply_id, user_id, vote) VALUES (?,?,?)', (reply_id, user_id, 0))


def update_vote(reply_id: int, user_id: int, vote):
    ''' Used to insert a new upvote/downvote value into votes in the database.'''

    if vote == 'upvote': vote = 1
    elif vote == 'downvote': vote = 0
    update_query('UPDATE votes SET vote = ? WHERE reply_id = ? and user_id = ?', (vote, reply_id, user_id))


def delete_vote(reply_id: int, user_id:int):
    ''' Used to delete a new upvote/downvote value into votes from the database.'''

    insert_query('DELETE FROM votes WHERE reply_id = ? AND user_id = ?', (reply_id, user_id))


def already_voted(reply_id, user_id, vote):
    ''' Used to check in the database if a reply is already upvoted/downvoted by the user.'''

    if vote == 'upvote': vote = 1
    elif vote == 'downvote': vote = 0

    if len(read_query('SELECT * FROM votes WHERE reply_id = ? AND user_id = ? AND vote = ?', (reply_id, user_id, vote))) > 0:
        return True
    else:
        return False


def different_vote(reply_id, user_id, vote):
    ''' Used to check in the database if a reply is upvoted/downvoted by the user so it can save the opposite vote and delete the value of the opposite value.'''

    if vote == 'upvote': vote = 1
    elif vote == 'downvote': vote = 0
    current_vote = read_query('SELECT vote FROM votes WHERE reply_id = ? AND user_id = ?', (reply_id, user_id))

    if len(current_vote) > 0:
        if current_vote[0] is not vote:
            return True
    else:
        return False



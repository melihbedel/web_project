_NOTE: This repository is a reupload of a group project, the original is privated and I do not have owner rights_

Project Description:

Design and implement a Forum System and provide RESTful API that can be consumed by different clients. High-level description:
• Users can read and create topics and message other users
• Administrators manage users, topics and categories

RESTful API Requirements
MUST Requirements:

Token Endpoint:
- Accepts user login data.
- Responds with authentication token that can be used to access other
endpoints.

Register User:
- Accepts user registration data.
- Consider making at least one user property unique for login purposes.

Create Topic:
- Requires authentication token.
- Topic data must contain at least a title and a Category.

Create Reply:
- Requires authentication token.
- Reply data should contain at least text and is associated with a specific Topic.

View Topics:
- Responds with a list of Topic resources.
- Consider adding search, sort and pagination query params.

View Topic:
- Responds with a single Topic resource and a list of Reply resources.

View Category:
- Responds with a list of all Topics that belong to that Category.
- Consider adding search, sort and pagination query params.

View Categories:
- Responds with a list of all Categories.

Create Message:
- Requires authentication.
- Creates a Message, should contain at least text as property.
 - Messages should be addressed to a specific user.

View Conversation:
- Requires authentication.
- Responds with a list of Messages exchanged between the authenticated user
and another user.

View Conversations:
- Requires authentication.
- Responds with a list of all Users with which the authenticated user has
exchanged messages.

Upvote/Downvote a Reply:
- Requires authentication.
- A user should be able to change their downvotes to upvotes and vice versa
but a reply can only be upvoted/downvoted once per user.

Choose Best Reply:
- Requires authentication.
- Topic Author can select one best reply to their Topic.

========================================================

SHOULD Requirements

Create Category:
- Requires admin authentication.
- Category data should contain at least a name.

Make Category Private / Non-private:
- Requires admin authentication.
- Changes visibility to a category and all associated topics.
- Topics in a private category are only available to category members.

Give User a Category Read Access:
- Requires admin authentication.
- A user can now view all Topics and Replies in the specific private Category.

Give User a Category Write Access:
- Requires admin authentication.
- A user can now view all Topics and Replies in the specific private Category and
post new Topics and Replies.

Revoke User Access:
- Requires admin authentication.
- A user loses their read or write access to a category.

View Privileged Users:
- Requires admin authentication.
- Responds with a list of all users for a specific Private Category along with their Access Level.

Lock Topic:
- Requires admin authentication.
- A Topic can no longer accept new Replies.

Lock Category:
- Requires admin authentication.
- A category can no longer accept new Topics.

========================================================

COULD Requirements:
Create a client that consumes your RESTful API.

========================================================

Guidelines

For each endpoint, your responsibility as a developer is to:
- Determine the URL.
- Decide on the HTTP method.
- Create the model for the request and response data.
- Think of necessary validations and error responses.

The Forum System consists of at least User, Topic, Category, Reply, and Message resources.
- Determine the necessary database structure.
- You are free to add as many properties/columns as you like, but the minimum.
required functionality must be supported.
- Determine the database relations.
- You are free to add as many tables, columns and relations as you need.

You are allowed to create new resources and endpoints if they fit the Forum System idea.

Start with the must Requirements and plan your time to implement as many should requirements as possible. It will be great to also create a web client, but it is the last of your tasks as it is a could requirement.
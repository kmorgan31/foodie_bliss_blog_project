# foodie_bliss_blog_project
A Python-Flask blog website.

Technologies used:
- Python - Flask
- SQLAlchemy
- PostgreSQL
- JQuery
- Bootstrap
- Jinja2
- HTML/CSS
- JavaScript - Ajax requests

Current Features:
- User management - Add New, Edit Profile
- User Validation & Verification (Signup and Login)
- Post management - Add, Edit, Delete
- Comment management - Add
- Subscriptions
  - Follow/Unfollow Users
    - View Followed on HomePage
    - View Followers, Followed from Profile
  - Favourite/Unfavourite Posts
    - View Favourited from Profile
- Filter Posts on HomePage by: 
  - Category
  - Subscribed Users
  - Favourited
  - Hot
  - Trending
  - Recent
  
- Search Posts by: 
  - Title

Optional Features:
- Comments - Edit, Delete
- Search Posts by Category


Setup:

1.  pip install -r requirements.txt
2.  Start postgresql service with username postgres password password
3.  Within psql, CREATE DATABASE foodieblissblog
4.  Run python create_database.py
5.  Run python run.py

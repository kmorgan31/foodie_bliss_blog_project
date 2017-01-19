from . import db
import datetime

class Post(db.Model):
    __tablename__ = "Post"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.String(1000))
    
    created_by = db.Column(db.Integer, db.ForeignKey("User.id"))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    
    
    def __init__(self,title,content,user_id):
        self.title = title
        self.content = content
        self.created_by = user_id
        
    comments = db.relationship('Comment', cascade='all,delete', backref='Post',lazy='dynamic')
        
class Comment(db.Model):
    __tablename__ = "Comment"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000))
    post_id = db.Column(db.Integer, db.ForeignKey("Post.id"))
    
    created_by = db.Column(db.Integer, db.ForeignKey("User.id"))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    
    
    def __init__(self,content,post_id,user_id):
        self.content = content
        self.post_id = post_id
        self.created_by = user_id
        
# class Favourite(db.Model):
#     __tablename__ = "Favourite"
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
#     favourite_user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    
#     created_by = db.Column(db.Integer, db.ForeignKey("User.id"))
#     created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    
    
#     def __init__(self,content,post_id,user_id):
#         self.content = content
#         self.post_id = post_id
#         self.created_by = user_id

class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(10))
    
    bio = db.Column(db.String(500))
    img_path = db.Column(db.String(500))
    twitter_url = db.Column(db.String(200))
    gplus_url = db.Column(db.String(200))
    fbk_url = db.Column(db.String(200))
    
    
    def __init__(self,username,email,password):
        self.username = username
        self.email = email
        self.password = password
        self.bio = "Tell me about yourself"
        self.img_path = "avatar.png"
    
    def __repr__(self):
        return "User " + self.username
        
    posts = db.relationship('Post', backref='User',lazy='dynamic')
    comments = db.relationship('Comment', backref='User',lazy='dynamic')
    # comments = db.relationship('Comment', backref='User',lazy='dynamic')
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
        

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('User.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('User.id'))
)


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
    
    posts = db.relationship('Post', backref='User',lazy='dynamic')
    comments = db.relationship('Comment', backref='User',lazy='dynamic')

    followed = db.relationship('User', 
                               secondary=followers, 
                               primaryjoin=(followers.c.follower_id == id), 
                               secondaryjoin=(followers.c.followed_id == id), 
                               backref=db.backref('followers', lazy='dynamic'), 
                               lazy='dynamic')
    
    def __init__(self,username,email,password):
        self.username = username
        self.email = email
        self.password = password
        self.bio = "Tell me about yourself"
        self.img_path = "avatar.png"
        self.twitter_url = ""
        self.gplus_url = ""
        self.fbk_url = ""
    
    def __repr__(self):
        return "User " + self.username
        
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
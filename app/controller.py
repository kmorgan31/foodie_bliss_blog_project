from app import app, db
from app.models import Post, User, Comment

import os
from flask import Flask
from flask import render_template #allow use of html templates
from flask import request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename


@app.route('/')
def index():
    username = get_currentusername()
    set_session_path("/")
    
    #get all posts
    post_list = []
    post_list = db.session.query(Post, User).join(User).filter(Post.created_by==User.id).order_by(Post.created_at.desc()).all()
    
    return render_template("index.html", username=username, post_list=post_list) #generates html based on template

@app.route('/about')
def about():
    username = get_currentusername()
    set_session_path("/about")
    return render_template("about.html", username=username) #generates html based on template

@app.route('/signup', methods=['GET','POST'])
def signup():
    username = get_currentusername()
    set_session_path("/signup")
    
    if request.method == 'POST':
        user = db.session.query(User).filter_by(username=request.form['username']).first()
        
        if(user):
            return redirect(url_for("login"))
        else:
            user = User(request.form['username'], request.form['email'], request.form['password']) #create User object from html fields
            db.session.add(user) #add to database
            db.session.commit() #save database
            
            user = db.session.query(User).filter_by(username=request.form['username'], password=request.form['password']).first()
            session['username'] = request.form['username']
            session['userid'] = user.id
            return redirect(url_for("index"))
            
    else:
        return render_template("signup.html", username=username) #generates html based on template
        
    
@app.route('/login', methods=['GET','POST'])
def login():
    username = get_currentusername()
    set_session_path("/login")
    
    if request.method == 'POST':
        user = db.session.query(User).filter_by(username=request.form['username'], password=request.form['password']).first()
        if (user):
            session['username'] = request.form['username']
            session['userid'] = user.id
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))
    else:
        return render_template("login.html", username=username) #generates html based on template
        
        
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route('/delete_post', methods=['POST'])
def delete_post():
    post = db.session.query(Post).filter_by(id=request.form['post_id']).first()
    db.session.delete(post) #add to database
    db.session.commit() #save database
    return redirect(session['path'])


@app.route('/add_post', methods=['GET','POST'])
def add_post():
    username = get_currentusername()
    # set_session_path("/add_post")
    
    if request.method == 'POST':
        user = db.session.query(User).filter_by(username=username).first()
        post= Post(request.form['title'], request.form['content'], user.id) #create Recipe object from html fields
        db.session.add(post) #add to database
        db.session.commit() #save database
        return redirect(session['path'])
    else:
        return render_template("post_page.html", username=username) #generates html based on template

@app.route('/add_comment', methods=['GET','POST'])
def add_comment():
    username = get_currentusername()
    # set_session_path("/add_post")
    
    if request.method == 'POST':
        user = db.session.query(User).filter_by(username=username).first()
        comment = Comment(request.form['content'], request.form['post_id'], user.id) #create Recipe object from html fields
        db.session.add(comment) #add to database
        db.session.commit() #save database
        return redirect(url_for('post', postid=request.form['post_id']))
    else:
        return render_template("comment_page.html", username=username) #generates html based on template


@app.route('/edit_post', methods=['GET','POST'])        
@app.route('/edit_post/<int:postid>', methods=['GET','POST'])
def edit_post(postid=None):
    username = get_currentusername()
    
    if(postid==None):
        postid = request.form['post_id']
        
    post = db.session.query(Post).filter_by(id=postid).first()
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit() #save database
        return redirect(session['path'])
    else:
        return render_template("post_page.html", username=username, post=post) #generates html based on template
        
@app.route('/edit_profile', methods=['POST'])        
def edit_profile():
    userid = request.form['user_id']
        
    user = db.session.query(User).filter_by(id=userid).first()
    user.username = request.form['username']
    user.email = request.form['email']
    user.bio = request.form['bio']
    user.twitter_url = request.form['twitter_url']
    user.gplus_url = request.form['gplus_url']
    user.fbk_url = request.form['fbk_url']

    file = request.files['file']

    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        filename = str(session['userid']) + "_" + secure_filename(file.filename)
        file.save(os.path.join(os.getcwd() + "/app/" + app.config['UPLOAD_FOLDER'], filename))
        user.img_path = filename
    
    db.session.commit() #save database
    return redirect(url_for('profile'))
    
        
@app.route('/post/<int:postid>')
def post(postid):
    username = get_currentusername()

    #get comments associated with post
    comment_list = db.session.query(Comment, User).filter_by(post_id=postid).join(User).filter(Comment.created_by==User.id).order_by(Comment.created_at.desc()).all()

    post = db.session.query(Post, User).filter_by(id=postid).join(User).filter(Post.created_by==User.id).first()
    return render_template("post.html", username=username, post=post, comment_list=comment_list) #generates html based on template


@app.route('/profile')
@app.route('/profile/<int:userid>')
def profile(userid=None):
    set_session_path("/profile")
    username = get_currentusername()
    
    if(userid==None):
        #get currentuserid
        userid = session['userid']

    # load user of selected user
    user = db.session.query(User).filter_by(id=userid).first()

    #get posts by current user
    post_list = db.session.query(Post, User).filter_by(created_by=userid).join(User).filter(Post.created_by==User.id).order_by(Post.created_at.desc()).all()

    #check if currentuser following selected user
    isFollowing = db.session.query(followers).filter_by(follower_id=session['userid'], followed_id=userid).first() > 0
    
    return render_template("profile.html", username=username, user=user, post_list=post_list) #generates html based on template

@app.route('/follow/<int:followed_id>')
def follow(followed_id):
    
    # load current user
    current_user = db.session.query(User).filter_by(id=session['userid']).first()
    
    # load user to follow
    follow_user = db.session.query(User).filter_by(id=followed_id).first()
    
    # append follow
    u = current_user.follow(follow_user)

    db.session.add(u)
    db.session.commit()
    flash('Following!')
    return redirect(url_for('profile', userid=followed_id))

@app.route('/unfollow/<int:followed_id>')
def unfollow(followed_id):
    
    # load current user
    current_user = db.session.query(User).filter_by(id=session['userid']).first()
    
    # load user to unfollow
    follow_user = db.session.query(User).filter_by(id=followed_id).first()
    
    u = current_user.unfollow(follow_user)

    db.session.add(u)
    db.session.commit()
    flash('Unfollowing!')
    return redirect(url_for('profile', userid=followed_id))

@app.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
    
@app.route('/settings')
def settings():
    username = get_currentusername()
    
    user = db.session.query(User).filter_by(id=session['userid']).first()
    return render_template("settings.html", username=username, user=user) #generates html based on template

def get_currentusername():
    if 'username' in session:
        user=session['username']
    else:
        user=None
    return user

def set_session_path(page):
    session['path'] = page

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

if __name__ == "__main__": #checks that we only run app when name is called directly (as main)
    app.run(host="0.0.0.0", port=8080, debug=True) #start webserver/app
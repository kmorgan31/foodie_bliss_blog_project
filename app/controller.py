from app import app, db
from app.models import Post, User, Comment, Tag, followers, tags_relationship, favourites_relationship

import os
from flask import Flask
from flask import render_template #allow use of html templates
from flask import request, redirect, url_for, session, send_from_directory, jsonify
from werkzeug.utils import secure_filename


@app.route('/')
def index():
    currentuser = get_currentuser()
    set_session_path("/")
    tag_list = get_tags()

     #if filtered
    if(request.args.get('filter_by')):
        filter_by=request.args.get('filter_by').encode('UTF8')

        q = db.session.query(Post, User).join(User).filter(Post.created_by==User.id)
        
        if(filter_by=="Subscribed"):
            q = q.join(followers, (followers.c.followed_id == User.id)).filter(followers.c.follower_id == currentuser.id)
            
        elif(filter_by=="Favourited"):
            q = q.join(favourites_relationship, (favourites_relationship.c.post_id == Post.id)).filter(favourites_relationship.c.user_id == currentuser.id)

        elif(filter_by!="None"): #category
            q = q.filter(Post.categories.any(Tag.name == filter_by))
        
        post_list = q.order_by(Post.created_at.desc()).all()
        
        return jsonify({'result': render_template('postlist.html', currentuser=currentuser, post_list=post_list, filter_by=filter_by)})
       
    else:
        #get all posts
        post_list = db.session.query(Post, User).join(User).filter(Post.created_by==User.id).order_by(Post.created_at.desc()).all()

        if(currentuser):
            user_list = db.session.query(User).join(followers, (followers.c.followed_id == User.id)).filter(followers.c.follower_id == currentuser.id).all()
        else:
            user_list = []
        
        return render_template("index.html", currentuser=currentuser, post_list=post_list, user_list=user_list,tag_list=tag_list, filter_by="None") #generates html based on template


@app.route('/about')
def about():
    currentuser = get_currentuser()
    set_session_path("/about")
    tag_list = get_tags()

    return render_template("about.html", currentuser=currentuser, tag_list=tag_list) #generates html based on template

@app.route('/signup', methods=['GET','POST'])
def signup():
    currentuser = get_currentuser()
    set_session_path("/signup")
    tag_list = get_tags()

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
        return render_template("signup.html", currentuser=currentuser, tag_list=tag_list) #generates html based on template
        
    
@app.route('/login', methods=['GET','POST'])
def login():
    currentuser = get_currentuser()
    set_session_path("/login")
    tag_list = get_tags()
    
    if request.method == 'POST':
        user = db.session.query(User).filter_by(username=request.form['username'], password=request.form['password']).first()
        if (user):
            session['username'] = request.form['username']
            session['userid'] = user.id
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))
    else:
        return render_template("login.html", currentuser=currentuser, tag_list=tag_list) #generates html based on template
        
        
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


@app.route('/add_post', methods=['POST'])
def add_post():
    currentuser = get_currentuser()
    tag_list = get_tags()
    # set_session_path("/add_post")
       
    selected_tag_ids = [x.encode('UTF8') for x in request.form.getlist('tag_dropdown')]
    post= Post(request.form['title'], request.form['content'], currentuser.id, selected_tag_ids) #create Recipe object from html fields
    db.session.add(post) #add to database
    db.session.commit() #save database
    return redirect(session['path'])


@app.route('/add_comment', methods=['POST'])
def add_comment():
    currentuser = get_currentuser()
    tag_list = get_tags()
    # set_session_path("/add_post")
    
    comment = Comment(request.form['content'], request.form['post_id'], currentuser.id) #create Recipe object from html fields
    db.session.add(comment) #add to database
    db.session.commit() #save database
    return redirect(url_for('post', postid=request.form['post_id']))


@app.route('/edit_post', methods=['GET','POST'])        
@app.route('/edit_post/<int:postid>', methods=['GET','POST'])
def edit_post(postid=None):
    currentuser = get_currentuser()
    tag_list = get_tags()
    
    if(postid==None):
        postid = request.form['post_id']
        
    post = db.session.query(Post).filter_by(id=postid).first()
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']

        #delete tags associated with post
        for tag in tag_list:
            t = post.remove_tag(tag)
            
            if(t!=None):
                db.session.add(t)
        
        #add tags selected by user
        selected_tag_names = [x.encode('UTF8') for x in request.form.getlist('tag_dropdown')]
        for tag_name in selected_tag_names:
            tag = db.session.query(Tag).filter_by(name=tag_name).first()
            t = post.add_tag(tag)
            db.session.add(t)

        db.session.commit() #save database
        return redirect(session['path'])
    else:
        selected_tag_names = [x.name.encode('UTF8') for x in post.get_post_tags()]
        return render_template("edit_post.html", currentuser=currentuser, post=post, tag_list=tag_list, selected_tag_names=selected_tag_names) #generates html based on template
     

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
    return redirect(url_for('profile', username=user.username))
    
        
@app.route('/post/<int:postid>')
def post(postid):
    currentuser = get_currentuser()
    tag_list = get_tags()

    #get selected post
    post = db.session.query(Post, User).filter_by(id=postid).join(User).filter(Post.created_by==User.id).first()

    #get comments associated with post
    comment_list = db.session.query(Comment, User).filter_by(post_id=postid).join(User).filter(Comment.created_by==User.id).order_by(Comment.created_at.desc()).all()

    return render_template("post.html", currentuser=currentuser, post=post, comment_list=comment_list, tag_list=tag_list) #generates html based on template

@app.route('/favourite/<int:postid>')
def favourite(postid):
    
    # load current user
    currentuser = get_currentuser()

    # load post to favourite
    post = db.session.query(Post).filter_by(id=postid).first()
    
    # append follow
    u = post.favourite(currentuser)

    db.session.add(u)
    db.session.commit()
    return redirect(url_for('post', postid=postid))

@app.route('/unfavourite/<int:postid>')
def unfavourite(postid):
    
    # load current user
    currentuser = get_currentuser()
    
    # load post to favourite
    post = db.session.query(Post).filter_by(id=postid).first()

    u = post.unfavourite(currentuser)

    db.session.add(u)
    db.session.commit()
    return redirect(url_for('post', postid=postid))

@app.route('/profile/<username>/following')
def get_profile_following(username):
    currentuser = get_currentuser()
    tag_list = get_tags()
    
    #get selected user
    selected_user = db.session.query(User).filter_by(username=username).first()

    #get following users
    user_list = db.session.query(User).join(followers, (followers.c.followed_id == User.id)).filter(followers.c.follower_id == selected_user.id).all()
    
    return render_template("userlist.html", currentuser=currentuser, selected_user=selected_user, user_list=user_list, tag_list=tag_list, source="Following")
    
    
@app.route('/profile/<username>/followers')
def get_profile_followers(username):
    currentuser = get_currentuser()
    tag_list = get_tags()

    #get selected user
    selected_user = db.session.query(User).filter_by(username=username).first()
    
    #get followers
    user_list = db.session.query(User).join(followers, (followers.c.follower_id == User.id)).filter(followers.c.followed_id == selected_user.id).all()
    
    return render_template("userlist.html", currentuser=currentuser, selected_user=selected_user, user_list=user_list, tag_list=tag_list, source="Followers")

@app.route('/profile/<username>')
def profile(username):
    set_session_path("/profile/"+username)
    currentuser = get_currentuser()
    tag_list = get_tags()
    
    if(username==currentuser.username): 
        #current user's profile selected
        user = currentuser
    else:
        # load user of selected user
        user = db.session.query(User).filter_by(username=username).first()

    #get posts and comments by current user
    post_list = db.session.query(Post, User).filter_by(created_by=user.id).join(User).filter(Post.created_by==User.id).order_by(Post.created_at.desc()).all()
    comment_list = db.session.query(Comment, Post, User).filter_by(created_by=user.id).join(Post).filter(Comment.post_id==Post.id).join(User).filter(Post.created_by==User.id).order_by(Comment.created_at.desc()).all()

    return render_template("profile.html", currentuser=currentuser, user=user, post_list=post_list, comment_list=comment_list, tag_list=tag_list) #generates html based on template

@app.route('/follow/<int:followed_id>')
def follow(followed_id):
    
    # load current user
    # current_user = db.session.query(User).filter_by(id=session['userid']).first()
    currentuser = get_currentuser()

    # load user to follow
    follow_user = db.session.query(User).filter_by(id=followed_id).first()
    
    # append follow
    u = currentuser.follow(follow_user)

    db.session.add(u)
    db.session.commit()
    return redirect(session['path'])

@app.route('/unfollow/<int:followed_id>')
def unfollow(followed_id):
    
    # load current user
    # current_user = db.session.query(User).filter_by(id=session['userid']).first()
    currentuser = get_currentuser()

    # load user to unfollow
    follow_user = db.session.query(User).filter_by(id=followed_id).first()
    
    u = currentuser.unfollow(follow_user)

    db.session.add(u)
    db.session.commit()
    return redirect(session['path'])

@app.route('/search', methods=['POST'])
def search():
    set_session_path("/search")
    currentuser = get_currentuser()
    tag_list = get_tags()
    
    query_string = request.form['query'].encode('UTF8')

    #get posts which contain query
    if(query_string!=""):
        post_list = db.session.query(Post, User).filter(Post.title.ilike('%{0}%'.format(query_string))).join(User).filter(Post.created_by==User.id).order_by(Post.created_at.desc()).all()
    else:
        post_list = db.session.query(Post, User).join(User).filter(Post.created_by==User.id).order_by(Post.created_at.desc()).all()
    
    return render_template("search.html", currentuser=currentuser, post_list=post_list, tag_list=tag_list, query_string=query_string) #generates html based on template

@app.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
    
@app.route('/settings')
def settings():
    currentuser = get_currentuser()
    tag_list = get_tags()
    
    return render_template("settings.html", currentuser=currentuser, tag_list=tag_list) #generates html based on template

def get_currentuser():
    if 'userid' in session:
        user = db.session.query(User).filter_by(id=session['userid']).first()
    else:
        user=None
    return user

def get_tags():
    tag_list = db.session.query(Tag).all()
    return tag_list

def set_session_path(page):
    session['path'] = page

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

if __name__ == "__main__": #checks that we only run app when name is called directly (as main)
    app.run(host="0.0.0.0", port=8080, debug=True) #start webserver/app
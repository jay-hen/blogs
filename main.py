from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogs:blogs@localhost:8889/blogs'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'ytjw495t0q3utq'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60))
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['index', 'login', 'signup', 'listings']
    if request.endpoint not in allowed_routes and 'user_id' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('home.html', web_title='Home, yo.', users=users)

@app.route('/blog', methods=['GET'])
def listings():
    if request.method == 'GET':
        #your_posts = Blog.query.filter_by(user_id=user_id)
        #return render_template('your_posts.html')
        
        post_id = request.args.get('id')
        owner_id = request.args.get('owner_id')
        blogs = Blog.query.order_by(Blog.id.desc()).all()

        if post_id:
            post = Blog.query.filter_by(id=post_id).first()
            return render_template("post.html", web_title=post.title, title=post.title, body=post.body, owner_id=post.owner.id, username=post.owner.username)
            # return render_template("post.html", web_title="{{post.title}}", blogs=blogs)
        if owner_id:
            your_posts = Blog.query.filter_by(owner_id=owner_id).all()
            return render_template('your_posts.html', your_posts=your_posts)
    
        return render_template("listings.html", web_title="Blog Listings", blogs=blogs)
    
@app.route('/new-post', methods=['GET', 'POST'])
def new_post():
    title = ''
    body = ''
    title_error = ''
    body_error = ''

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if not title:
            title_error = "Be sure to enter a title!"

        if not body:
            body_error = "Type a post! That's the whole point!"

        if not title_error and not body_error:
            user_id = session['user_id']
            owner = User.query.get(user_id)
            new_entry = Blog(title, body, owner)
            db.session.add(new_entry)
            db.session.commit()
            post_id = new_entry.id

            return redirect('/blog?id={}'.format(post_id))
        else:
            return render_template("form.html", web_title="Create a New Post", title=title, title_error=title_error, body=body, body_error=body_error)

    if request.method == 'GET':
        return render_template("form.html", web_title="Create a New Post")

@app.route('/signup', methods= ['POST', 'GET'])
def signup():

    if request.method == 'GET':
        return render_template('signup.html', web_title='Create an Account!', username='', name_error='', password='', password_error='', verify='', verify_error='')

    if request.method == 'POST':
        username = cgi.escape(request.form['username'])
        password = cgi.escape(request.form['password'])
        verify = cgi.escape(request.form['verify'])


        name_error = ""
        password_error = ''
        verify_error = ''


        if not username:
            name_error = "Please, enter a username."
        elif len(username) < 3 or len(username) > 20:
            name_error = "Your username must be between 3 and 20 characters."
        else:
            for char in username:
                if char.isspace():
                    name_error = "Your username cannot contain spaces."

        if not password:
            password_error = "Please, enter a password."
        elif len(password) < 3 or len(password) > 20:
            password_error = "Your password must be between 3 and 20 characters."
        else:
            for char in password:
                if char.isspace():
                    password_error = "Your password cannot contain spaces."

        if password != verify:
            verify_error = "Your passwords need to match."

        if not name_error and not password_error and not verify_error:
            new_account = User(username, password)
            db.session.add(new_account)
            db.session.commit()
            session['user_id'] = new_account.id
            return redirect('/new-post?id={}'.format(new_account.id))            

        return render_template('signup.html', web_title='Create an Account!', username=username, name_error=name_error, password=password, password_error=password_error, verify=verify, verify_error=verify_error)

@app.route('/login', methods=['get', 'POST'])
def login():
    if request.method == 'GET': 
        return render_template('login.html')
        
    if request.method == 'POST':
    
        name_error = ''
        password_error = ''
        username = cgi.escape(request.form['username'])
        password = cgi.escape(request.form['password'])
        user = User.query.filter_by(username=username).first()   

        if not username:
            name_error = "You know you need a username, right?"
        if not password:
            password_error = "You should really have a password."
        if not name_error and not password_error:
            if password == user.password:
                session['user_id'] = user.id
                return redirect('/new-post?id={}'.format(user.id))
            else:
                password_error = "I'm pretty sure you exist, but that isn't your password."

        return render_template('login.html', username=username, name_error=name_error, password=password, password_error=password_error)

@app.route('/logout', methods=['Get'])
def logout():
    del session['user_id']
    flash('You logged out!')
    return redirect('/blog')

if __name__ == '__main__':
    app.run()
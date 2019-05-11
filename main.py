from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

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
    username = (db.String(60))
    password = (db.String(30))
    blogs = db.relationship('Blog', backref='owner')

def __init_(self, username, password):
    self.username = username
    self.password = password

@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def listings():

    post_id = request.args.get('id')

    if post_id == None:
        blogs = Blog.query.all()
        return render_template("listings.html", web_title="Blog Listings", blogs=blogs)
    else:
        post = Blog.query.get(post_id)
        return render_template('post.html', post=post, web_title="{{post.title}}")

@app.route('/new-post', methods=['GET', 'POST'])
def new_post():
    title = ''
    body = ''
    owner = ''
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
            new_entry = Blog(title, body)
            db.session.add(new_entry)
            db.session.commit()

            return redirect('/blog?id={}'.format(new_entry.id))
        else:
            return render_template("form.html", web_title="Create a New Post", title=title, title_error=title_error, body=body, body_error=body_error)

    if request.method == 'GET':
         return render_template("form.html", web_title="Create a New Post")

@app.route('/signup', methods= ['get'])
def signup():
    return render_template('signup.html', web_title='Create an Account!')

@app.route('/login', methods=['get'])
def login():
    return render_template('login.html', web_title='Go on and Log in!')

if __name__ == '__main__':
    app.run()
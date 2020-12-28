from flask import Flask, session, request, jsonify
# from flask_session import session
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy  
from flask_cors import CORS
from flask_marshmallow import Marshmallow 
from flask_admin.contrib.sqla import ModelView 
from flask_basicauth import BasicAuth
from flask_bcrypt import Bcrypt
from datetime import timedelta
import marshmallow_sqlalchemy
import os 

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
# app.config['BASIC_AUTH_FORCE'] = True
# app.config['BASIC_AUTH_USERNAME'] = 'Danielle'
# app.config['BASIC_AUTH_PASSWORD'] = 'password'
# app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
db = SQLAlchemy(app)
ma = Marshmallow(app)
# basic_auth = BasicAuth(app)
# admin = Admin(app)
flask_bcrypt = Bcrypt(app)
# admin.add_view(ModelView(User, db.session))
# admin.add_view(ModelView(Post, db.session))
app.secret_key = os.environ.get('SECRET_KEY')
app.permanent_session_lifetime = timedelta(minutes=5)
CORS(app, supports_credentials=True)


CORS(app)

class Post(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(50))
  author = db.Column(db.String(25))
  content = db.Column(db.Text)

  def __init__(self, title, author, content):
    self.title = title
    self.author = author
    self.content = content
  
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(25))
  password = db.Column(db.String(40))
 

  def __init__(self, name, password):
    self.name = name
    self.password = password
  
  

class PostSchema(ma.Schema):
  class Meta:
    fields = ("id", "title", "author", "content")

class UserSchema(ma.Schema):
  class Meta:
    fields = ("id", "name", "password")

post_schema = PostSchema()
posts_schema = PostSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)


# @app.route('/secret')
# @basic_auth.required
# def secret_view():
#   return "login"
  

@app.route("/")
def hello():
  return "hello"

@app.route('/logged-in', methods=['GET'])
def logged_in():
  print(session)
  if 'name' in session:
    db_user = User.query.filter_by(name=session['name']).first()
    print(db_user)
    if db_user: 
      return jsonify('User Loggedin Via Cookie')
    else: 
      return jsonify('Session exists, but user does not exist (anymore)')
  else: 
    return jsonify('nope')

@app.route('/login', methods=['POST'])
def login():
  post_data = request.get_json()
  db_user = User.query.filter_by(name=post_data.get('name')).first()
  if db_user is None: 
    return jsonify('Name NOT found')
  password = post_data.get('password')
  db_user_hashed_password = db_user.password
  valid_password = flask_bcrypt.check_password_hash(db_user_hashed_password, password)
  if valid_password:
    session.permanent = True
    session['name'] = post_data.get('name')
    return jsonify('User Verified')
  return jsonify('Password is not corret')


@app.route('/register', methods=['POST'])
def register():
  post_data = request.get_json()
  db_user = User.query.filter_by(name=post_data.get('name')).first()
  if db_user:
    return jsonify('Name taken')
  name = post_data.get('name')
  email = post_data.get('email')
  password = post_data.get('password')
  hashed_password = flask_bcrypt.generate_password_hash(password).decode('utf-8') 
  new_user = User(name=name, password=hashed_password)
  db.session.add(new_user)
  db.session.commit()
  session.permanent = True
  session['name'] = post_data.get('name')
  return jsonify("User Created!")


# USERS

@app.route("/user/<id>", methods=["DELETE"])
def delete_user(id):
  record = User.query.get(id)
  db.session.delete(record)
  db.session.commit()

  return jsonify("USER DELETED")

@app.route("/user/<id>", methods=["PATCH"])
def update_user(id):
  user = User.query.get(id)
  rqt = request.get_json(force=True)

  new_name = rqt["name"]
  new_email = rqt["email"]
  new_password = rqt["password"]
  new_admin = rqt["admin"]

  user.name = new_name
  user.email = new_email
  user.password = new_password
  user.admin = new_admin
  
  db.session.commit()
  print(user_schema.jsonify(user))
  return user_schema.jsonify(user)

@app.route("/users", methods=["GET"])
def get_users():
  all_users = User.query.all()
  result = users_schema.dump(all_users)
  return jsonify(result)


@app.route("/add-user", methods=["POST"])
def add_user():
  rqt = request.get_json(force=True)

  name = rqt["name"]
  email = rqt["email"]
  password = rqt["password"]
  admin = rqt["admin"]

  record = User(name, email, password, admin)
  db.session.add(record)
  db.session.commit()

  user = User.query.get(record.id)
  return user_schema.jsonify(user)


# POSTS

@app.route("/post/<id>", methods=["GET"])
def get_post(id):
  post = Post.query.get(id)
  result = post_schema.dump(post)
  return jsonify(result)

@app.route("/posts", methods=["GET"])
def get_posts():
  all_posts = Post.query.all()
  result = posts_schema.dump(all_posts)
  return jsonify(result)

@app.route("/add-post", methods=["POST"])
def add_post():
  rqt = request.get_json(force=True)
  
  title = rqt["title"]
  author = rqt["author"]
  content = rqt["content"]

  record = Post(title, author, content)
  
  db.session.add(record)
  db.session.commit()

  post = Post.query.get(record.id)
  return post_schema.jsonify(post)

@app.route("/post/<id>", methods=["PATCH"])
def update_post(id):
  post = Post.query.get(id)
  rqt = request.get_json(force=True)

  new_title = rqt["title"]
  new_author = rqt["author"]
  new_content = rqt["content"]

  post.title = new_title
  post.author = new_author
  post.content = new_content
  
  db.session.commit()
  print(post_schema.jsonify(post))
  return post_schema.jsonify(post)

@app.route("/post/<id>", methods=["DELETE"])
def delete_post(id):
  record = Post.query.get(id)
  db.session.delete(record)
  db.session.commit()

  return jsonify("POST DELETED")

if __name__ == '__main__':
  db.create_all()
  app.run(debug=True)
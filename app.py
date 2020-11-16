from flask import Flask, request, jsonify 
from flask_sqlalchemy import SQLAlchemy  
from flask_cors import CORS
from flask_marshmallow import Marshmallow 
import marshmallow_sqlalchemy
import os 

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

CORS(app)

class Post(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(50))
  content = db.Column(db.Text)

  def __init__(self, title, content):
    self.title = title
    self.content = content

class Comment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer)
  content = db.Column(db.Text)
  post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

  def __init__(self, user_id, post_id, content):
    self.user_id = user_id
    self.post_id = post_id
    self.content = content
  

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(25))
  email = db.Column(db.String(40))
  password = db.Column(db.String(40))
  admin = db.Column(db.Boolean)

  def __init__(self, name, email, password, admin):
    self.name = name
    self.email = email
    self.password = password
    self.admin = admin
  

class PostSchema(ma.Schema):
  class Meta:
    fields = ("id", "title", "content", "user_id", "post_id", "post", "name", "comment")

class CommentSchema(ma.Schema):
  class Meta:
    fields = ("id", "user_id", "post_id", "content")

class UserSchema(ma.Schema):
  class Meta:
    fields = ("id", "name", "email", "password", "admin")

post_schema = PostSchema()
posts_schema = PostSchema(many=True)

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)


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

# COMMENTS

@app.route("/comment/<id>", methods=["DELETE"])
def delete_comment(id):
  record = Comment.query.get(id)
  db.session.delete(record)
  db.session.commit()

  return jsonify("COMMENT DELETED")

@app.route("/comment/<id>", methods=["PATCH"])
def update_comment(id):
  comment = Comment.query.get(id)
  rqt = request.get_json(force=True)

  new_content = rqt["content"]

  comment.content = new_content
  
  db.session.commit()
  print(comment_schema.jsonify(comment))
  return comment_schema.jsonify(comment) 

@app.route("/comments", methods=["GET"])
def get_comments():
  all_comments = Comment.query.all()
  result = comments_schema.dump(all_comments)
  return jsonify(result)

@app.route("/add-comment/<id>", methods=["POST"])
def add_comment(id):
  rqt = request.get_json(force=True)

  user_id = rqt["user_id"]
  post_id = rqt["post_id"]
  content = rqt["content"]

  record = Comment(user_id, post_id, content)

  db.session.add(record)
  db.session.commit()

  comment = Comment.query.get(record.id)
  return comment_schema.jsonify(comment)

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
  content = rqt["content"]

  record = Post(title, content)
  
  db.session.add(record)
  db.session.commit()

  post = Post.query.get(record.id)
  return post_schema.jsonify(post)

@app.route("/post/<id>", methods=["PATCH"])
def update_post(id):
  post = Post.query.get(id)
  rqt = request.get_json(force=True)

  new_title = rqt["title"]
  new_content = rqt["content"]

  post.title = new_title
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
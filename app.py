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
  post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
  post = db.relationship('Post',
        backref=db.backref('comments', lazy=True))

  def __init__(self, user_id, post_id, post):
    self.user_id = user_id
    self.post_id = post_id
    self.post = post
  

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(25))

  def __init__(self, name):
    self.name = name
  

class PostSchema(ma.Schema):
  class Meta:
    fields = ("id", "title", "content")

post_schema = PostSchema()
posts_schema = PostSchema(many=True)

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

  return jsonify("RECORD DELETED")

if __name__ == '__main__':
  db.create_all()
  app.run(debug=True)
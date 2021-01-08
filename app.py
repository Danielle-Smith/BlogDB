from flask import Flask, render_template, redirect, url_for, jsonify, request, session, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, Form, TextField, TextAreaField, SubmitField, validators, ValidationError
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_marshmallow import Marshmallow
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from datetime import timedelta
from flask_cors import CORS
from flask_mail import Mail, Message
import smtplib
import socket
import os



app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.permanent_session_lifetime = timedelta(minutes=5)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
# app.config['MAIL_SERVER'] = "smtp.mail.yahoo.com"
# app.config["MAIL_PORT"] = 465
# app.config["MAIL_USE_SSL"] = True
# # app.mail_username = os.environ.get('mail_username')
# # app.mail_password = os.environ.get('mail_password')
# app.config["MAIL_USERNAME"] = 'dani.dimo@yahoo.com'
# app.config["MAIL_PASSWORD"] = 'DaniYahoo#1'




bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.permanent_session_lifetime = timedelta(minutes=5)
CORS(app)

mail = Mail(app)
socket.getdefaulttimeout()



class Post(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(50))
  author = db.Column(db.String(25))
  content = db.Column(db.Text)

  def __init__(self, title, author, content):
    self.title = title
    self.author = author
    self.content = content

  
class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(25), unique=True, nullable=False)
  email = db.Column(db.String(50), unique=True)
  password = db.Column(db.String(200), nullable=False)
 

  def __init__(self, username, email, password):
    self.username = username
    self.email = email
    self.password = password

class Contact(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(25))
  email = db.Column(db.String(50))
  message = db.Column(db.String(500))

  def __init__(self, name, email, message):
    self.name = name
    self.email = email
    self.message = message


class MyModelView(ModelView):
  def is_accessible(self):
    return current_user.is_authenticated

  def inaccessible_callback(self, name, **kwargs):
      return redirect(url_for('/login'))

class MyAdminIndexView(AdminIndexView):
  def is_accessible(self):
    return current_user.is_authenticated

  def inaccessible_callback(self, name, **kwargs):
      return redirect(url_for('login'))

    
admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Post, db.session))


class PostSchema(ma.Schema):
  class Meta:
    fields = ("id", "title", "author", "content")

class UserSchema(ma.Schema):
  class Meta:
    fields = ("id", "username", "email", "password")

class ContactSchema(ma.Schema):
  class Meta:
    fields = ("id", "name", "email", "message")

post_schema = PostSchema()
posts_schema = PostSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

contact_schema = ContactSchema()
contacts_schema = ContactSchema(many=True)



@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=3, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=3, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)]) 

# class ContactForm(Form):
#   name = TextField("Name",  [validators.Required("Please enter your name.")])
#   email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
#   message = TextAreaField("Message",  [validators.Required("Please enter a message.")])

class ContactForm(FlaskForm):
  name = TextField("Name",  [validators.DataRequired("Please enter your name.")])
  email = TextField("Email",  [validators.DataRequired("Please enter your email address."), validators.Email("Please enter your email address.")])
  subject = TextField("Subject",  [validators.DataRequired("Please enter a subject.")])
  message = TextAreaField("Message",  [validators.DataRequired("Please enter a message.")])
  submit = SubmitField("Send")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
  s = smtplib.SMTP('smtp.mail.yahoo.com', 465)
  s.ehlo()
  s.starttls()
  s.login('dani.dimo@yahoo.com', 'DaniYahoo#1')
  form = ContactForm()
 
  if request.method == 'POST':
    if form.validate() == False:
     
      return render_template('contact.html', form=form)
    else:
      msg = Message(form.subject.data, sender='smtp.mail.yahoo.com', recipients=['danielle@natesdesign.com'])
      msg.body = """
      From: %s <%s>
      %s
      """ % (form.name.data, form.email.data, form.message.data)
      mail.send(msg)
 
      return 'Form posted.'
 
  elif request.method == 'GET':
    return render_template('contact.html', form=form)

 
  # if request.method == 'POST':
  #   if form.validate() == False:
  #     return ('All fields are required.')
      
  #   else:
  # msg = Message(form.message.data, sender='dani.dimo@yahoo.com', recipients=['danielle@natesdesign.com'])
 
  # mail.send(msg)

  # return ('Form posted.')
  # return("Didn't work")
 
  
@app.route('/logged-in', methods=['GET'])
def logged_in():
  print(session)
  if 'username' in session:
    db_user = User.query.filter_by(username=session['username']).first()
    print(db_user)
    if db_user: 
      return jsonify('User Loggedin Via Cookie')
    else: 
      return jsonify('Session exists, but user does not exist (anymore)')
  else: 
    return jsonify('nope')

@app.route('/api/delete-user/<id>', methods=['DELETE'])
def api_delete_user(id):
  user = User.query.filter_by(id=id).first()
  db.session.delete(user)
  db.session.commit()
  return jsonify('user deleted')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('user.details_view'))

        return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)
 

@app.route('/logout', methods=['GET', 'POST'])
def logout():
  logout_user()
  session.clear()
  return jsonify('Logged Out')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'
        

    return render_template('signup.html', form=form)


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

  username = rqt["username"]
  password = rqt["password"]
  

  record = User(username, password)
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
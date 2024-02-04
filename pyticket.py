from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user
from flask_login import login_required
from flask_login import logout_user
from flask_login import current_user
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms import validators
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms_alchemy import QuerySelectField
from datetime import datetime

#init the Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_db.db'
app.secret_key = "b'\xb2\xa6fR\x0c\x1d\xf8\xe1@\xd5\xe1\xe4\x88\xc8l\xbe'"

#init SQLite db
db = SQLAlchemy(app)

#init Bcrypt for pass hash
bcrypt = Bcrypt(app)

#init LoginManager from flask_login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

#user model for db
#is_auth(), is_active(), is_anonymous(), and get_id() are required for flask_login
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), unique=False, nullable=False)

    def is_authenticated():
        return True
    
    def is_active():
        return True

    def is_anonymous():
        return False

    def get_id(self):
        return str(self.id)

#ticket model for db
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignee = db.Column(db.String(20), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

#connects to fields within register.html
class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=6)])
    confirm_password = PasswordField('Confirm Password', [validators.DataRequired(), validators.EqualTo('password')])
    submit = SubmitField('Register')

#connects to fields within login.html
class LoginForm(FlaskForm):
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])
    submit = SubmitField('Login')

#query that returns all users, currently used for assignee field in CreateTicketForm class
def get_users():
    return User.query.all()

#connects to fields within create-ticket.html
class CreateTicketForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    assignee = QuerySelectField('Assignee', query_factory=get_users, get_label='username', allow_blank=False, validators=[DataRequired()])
    submit = SubmitField('Create Ticket')

#needed for flask_login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Email address is already taken. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')

    return render_template('login.html', form=form)

@app.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username, email=current_user.email)

@app.route('/create-ticket/', methods=['GET', 'POST'])
@login_required
def create_ticket():
    form = CreateTicketForm()

    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        assignee = form.assignee.data.id  # Use user.id for assignee

        new_ticket = Ticket(title=title, description=description, assignee=assignee, creator_id=current_user.id)
        db.session.add(new_ticket)
        db.session.commit()

        flash('Ticket created successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('create-ticket.html', form=form)

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False)
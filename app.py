from flask import Flask, url_for, render_template, session, redirect, flash, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pymongo
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
app.secret_key = "b'\xb2\xa6fR\x0c\x1d\xf8\xe1@\xd5\xe1\xe4\x88\xc8l\xbe'"

#**************************************************Database*****************************************************************
client = pymongo.MongoClient('localhost', 27017)
db = client.user_login_system
app.config["MONGO_URI"] = "mongodb+srv://sullyelh:Riordan202@pyticketuserdb.nf8yle6.mongodb.net/?retryWrites=true&w=majority"
login_manager = LoginManager(app)
login_manager.login_view = 'login'

#**************************************************User Stuff*****************************************************************
class User(UserMixin):

    def __init__(self, user_id, email):
        self.id = user_id
        self.email = email
    
    def is_authenticated(self):
        True

    def is_active(self):
        True

    def is_anonymous(self):
        False

    def get_id(self):
        return str(self.id)

#**************************************************Sessions***************************************************************
def start_session():
    session['user'] = user
#**************************************************Routes*****************************************************************

@app.route("/")
def home():
    if current_user.is_authenticated:
        return render_template('home.html')
    else:
        return render_template('anon-home.html')

@app.route("/register/", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']

        hashed_password = generate_password_hash(password, method="sha256")

        user_data= {
            '_id': uuid.uuid4().hex,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': hashed_password
        }
        if db.users.find_one({ "email": user_data['email'] }):
            return jsonify({ "error": "Email address already in use." })
        result = db.users.insert_one(user_data)
        if result.inserted_id:
            return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/dashboard/")
@login_required
def dashboard():
    return render_template("dashboard.html")


@login_manager.user_loader
def load_user(user_id):
    user_data = db.users.find_one({ '_id': user_id })
    if user_data:
        return User(user_id = user_data['_id'], email = user_data['email'])
    return None

@app.route("/login/", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        

        user = db.users.find_one({ 'email': email })
        if user and check_password_hash(user['password'], password):
            user_obj = User(user_id = user['_id'], email = user['email'])
            login_user(user_obj)
            return redirect(url_for("dashboard"))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/my_account')
@login_required
def my_account():
    return render_template('my-account.html', current_user = current_user)
#**************************************************Run*****************************************************************
if __name__ == "__main__":
    app = create_app()
    app.config['DEBUG'] = True

    app.run()
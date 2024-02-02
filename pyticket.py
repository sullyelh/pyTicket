from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_db.db'
app.secret_key = "b'\xb2\xa6fR\x0c\x1d\xf8\xe1@\xd5\xe1\xe4\x88\xc8l\xbe'"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), unique=False, nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.id}')"


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register/')
def register():
    return render_template('register.html')

@app.route('/login/')
def login():
    return render_template('login.html')

@app.route('/test_db')
def test_db():
    test_user = User(username='TestUser', email='testuser@example.com', password='testpassword')
    db.session.add(test_user)
    db.session.commit()
    return "Test Passed"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False)


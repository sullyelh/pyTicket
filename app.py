from flask import Flask, url_for, render_template, session, redirect, flash, request, jsonify
from flask import url_for
from flask import render_template
from flask import redirect
from flask import jsonify
import pymongo
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "b'\xb2\xa6fR\x0c\x1d\xf8\xe1@\xd5\xe1\xe4\x88\xc8l\xbe'"

client = pymongo.MongoClient('localhost', 27017)
db = client.user_login_system
app.config["MONGO_URI"] = "mongodb+srv://sullyelh:Riordan202@pyticketuserdb.nf8yle6.mongodb.net/?retryWrites=true&w=majority"

@app.route("/")
def home():
    return render_template('home.html')


@app.route("/register/", methods=['GET', 'POST'])
def register():
    return render_template("register.html")

@app.route("/dashboard/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/login/", methods=['POST', 'GET'])
def login():
    return render_template('login.html')


#**************************************************Run*****************************************************************
if __name__ == "__main__":
    app = create_app()
    app.config['DEBUG'] = True

    app.run()
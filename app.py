from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zangyo.sqlite'

db = SQLAlchemy(app)
class Overtime(db.Model):

    __tablename__ = "overtimes"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.Integer)
    date = db.Column(db.String())
    time = db.Column(db.Float())
    total_time = db.Column(db.Float())

db.create_all()

@app.route('/')
def index():
    overtimes = Overtime.query.all()
    return render_template("index.html", overtimes = overtimes)

@app.route('/new', methods=["POST"])
def new():
    overtime = Overtime()
    overtime.date = request.form["new_date"]
    overtime.time = request.form["new_text"]
    overtime.total_time = 1 # 仮で1
    overtime.status = 0
    db.session.add(overtime)
    db.session.commit()
    return redirect(url_for('index'))

app.run(debug=True, host=os.getenv('APP_ADDRESS', 'localhost'), port=8001)

# test

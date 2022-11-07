from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import desc #降順に並べ替えの時に必要
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zangyo.sqlite'

# データベースの作成
db = SQLAlchemy(app)
class Overtime(db.Model):

    __tablename__ = "overtimes"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.Integer)
    date = db.Column(db.String())
    time = db.Column(db.Float())
    total_time = db.Column(db.Float())

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    overtimes = Overtime.query.order_by(Overtime.date).all() # 日付を昇順に並べ替え
    db.session.commit()
    # overtimes = Overtime.query.all()
    return render_template("index.html", overtimes = overtimes)

@app.route('/delete')
def delete():
    Overtime.query.delete() # Overtimeデータベース削除
    db.session.commit()
    return render_template("index.html")

@app.route('/new', methods=["POST"])
def new():
    overtime = Overtime()
    overtime.date = request.form["new_date"]
    overtime.time = float(request.form["new_text"])
    totals = db.session.query(Overtime.time).all()
    sum = 0
    print(totals)
    for total in totals:
        sum = sum + total[0]
    overtime.total_time = sum + overtime.time
    overtime.status = 0
    db.session.add(overtime)
    db.session.commit()
    return redirect(url_for('index'))

app.run(debug=True, host=os.getenv('APP_ADDRESS', 'localhost'), port=8001)
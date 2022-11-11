from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import desc #降順に並べ替えの時に必要
import os
import datetime

print("run")

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
    time_36 = db.Column(db.Float())

# with app.app_context():
#     db.create_all()

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'GET':
        overtimes = Overtime.query.order_by(Overtime.date).all() # 日付を昇順に並べ替え
        db.session.commit()
        # overtimes = Overtime.query.all()
        return render_template("index.html", overtimes = overtimes)
    else:
        print('update')
        for i in range(30):
            overtime = db.session.query(Overtime).filter(Overtime.id==(i+1)).first()
            overtime.time = float(request.form["time_{}".format(i+1)])
        db.session.commit()
        print('total_time')
        sum =0 
        for i in range(30):
            overtime = db.session.query(Overtime).filter(Overtime.id==(i+1)).first()
            overtime.total_time = sum + overtime.time
            sum = overtime.total_time
            db.session.commit()
        return redirect(url_for('index'))

@app.route('/delete')
def delete():
    # Overtimeデータベース削除
    Overtime.query.delete()
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/create', methods=["GET"])
def create():
    print('create')
    # 2022/4/1から1日づつ30個データを作成　初期値は全て0
    overtime = [Overtime(status = 0, time = 0, date = datetime.date(2022, 4, i+1), total_time = 0 ,time_36 = 0) for i in range(30)] 
    db.session.add_all(overtime)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/new', methods=["POST"])
def new():
    overtime = Overtime()
    overtime.date = request.form["new_date"]
    overtime.time = float(request.form["new_text"])
    totals = db.session.query(Overtime.time).all()
    sum = 0
    for total in totals:
        sum = sum + total[0]
    overtime.total_time = sum + overtime.time
    overtime.status = 0
    overtime.time_36 = 1
    db.session.add(overtime)
    db.session.commit()
    return redirect(url_for('index'))

app.run(debug=True, host=os.getenv('APP_ADDRESS', 'localhost'), port=8001)
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
    weekday = db.Column(db.Integer)
    time = db.Column(db.Float())
    total_time = db.Column(db.Float())
    time_36 = db.Column(db.Float())

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'GET':
        with app.app_context():
            db.create_all()
        overtimes = Overtime.query.order_by(Overtime.date).all() # 日付を昇順に並べ替え
        db.session.commit()
        return render_template("index.html", overtimes = overtimes)
    else:
        print('update')
        date_count = Overtime.query.count() # データベースのデータ数
        print(date_count)
        sum =0 
        for i in range(date_count):
            overtime = db.session.query(Overtime).filter(Overtime.id==(i+1)).first()
            overtime.time = float(request.form["time_{}".format(i+1)])
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

@app.route('/create', methods=["GET", "POST"])
def create():
    if request.method == 'GET':
        print('create')
        return render_template("create.html")
    else:
        print('create_date')
        create_date = request.form["create_date"] #create_dateを読み込み
        create_date = datetime.datetime.strptime(create_date, '%Y-%m-%d') #型変換
        create_date = datetime.date(create_date.year, create_date.month, create_date.day) #年月日だけに変換
        last_date = request.form["last_date"] #last_dateを読み込み
        last_date = datetime.datetime.strptime(last_date, '%Y-%m-%d') #型変換
        last_date = datetime.date(last_date.year, last_date.month, last_date.day) #年月日だけに変換
        print(create_date, last_date)
        # print(type(create_date))
        for i in range(31):
            date = create_date + datetime.timedelta(days=i)
            overtime = [Overtime(
                status = 0,
                date = date,
                weekday = date.weekday(),
                time = 0, total_time = 0 ,time_36 = 0)] 
            db.session.add_all(overtime)
            if date == last_date:
                break
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
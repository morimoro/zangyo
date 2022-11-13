#残業を管理するアプリ

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
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

    #データベースのテーブル名
    __tablename__ = "overtimes"
    #データベースの要素
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.Integer)
    date = db.Column(db.String())
    weekday = db.Column(db.Integer)
    time = db.Column(db.Float())
    holiday_time = db.Column(db.Float())
    total_time = db.Column(db.Float())
    time_36 = db.Column(db.Float())
    estimated_time = db.Column(db.Float())

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'GET':
        with app.app_context():
            db.create_all()
        overtimes = Overtime.query.order_by(Overtime.date).all() # 日付を昇順に並べ替え
        db.session.commit()
        scheduled_overtime = 0 #月間予定残業に初期値として0を代入
        last_month_36_overtime = 0  #前月最終日36残業時間に初期値として0を代入
        working_days = 0 #月間稼働日に初期値として0を代入
        return render_template("index.html",
        overtimes = overtimes, scheduled_overtime=scheduled_overtime, last_month_36_overtime=last_month_36_overtime, working_days=working_days)

    else:
        print('update')
        date_count = Overtime.query.count() # データベースのデータ数
        print(date_count)

        #月間予定残業を取得、未入力なら0を代入
        try:
            scheduled_overtime = float(request.form["scheduled_overtime"])
        except:
            scheduled_overtime = 0
        
        #前月最終日36残業時間を取得、未入力なら0を代入
        try:
            last_month_36_overtime = float(request.form["last_month_36_overtime"])
            sum_36 = last_month_36_overtime 
        except:
            last_month_36_overtime = 0
            sum_36 = db.session.query(Overtime).filter(Overtime.id==1).first().time_36 - db.session.query(Overtime).filter(Overtime.id==1).first().time

        # データベースの回数だけ繰り返し、値を取得して月間残業、36残業を計算
        sum = 0
        for i in range(date_count):
            overtime = db.session.query(Overtime).filter(Overtime.id==(i+1)).first()
            overtime.status = int(request.form["status_{}".format(i+1)])
            overtime.time = float(request.form["time_{}".format(i+1)])
            overtime.holiday_time = float(request.form["holiday_time_{}".format(i+1)])
            overtime.total_time = sum + overtime.time + overtime.holiday_time
            sum = overtime.total_time
            overtime.time_36 = sum_36 + overtime.time
            # もし15日ならsum_36=0、16日は0から足し算開始
            if datetime.datetime.strptime(overtime.date, '%Y-%m-%d').day == 15:
                sum_36 = 0
            else:
                sum_36 = overtime.time_36
            db.session.commit()
        with app.app_context():
            db.create_all()
        overtimes = Overtime.query.order_by(Overtime.date).all() # 日付を昇順に並べ替え
        db.session.commit()

        working_days = db.session.query(Overtime).filter(Overtime.status==1).count()
        ave_estimated_time = scheduled_overtime / working_days
        sum_estimated_time = 0
        for i in range(date_count):
            overtime = db.session.query(Overtime).filter(Overtime.id==(i+1)).first()
            if overtime.status == 1:
                overtime.estimated_time = sum_estimated_time + ave_estimated_time
                sum_estimated_time = overtime.estimated_time
            else:
                overtime.estimated_time = sum_estimated_time
        db.session.commit()

        return render_template("index.html",
        overtimes = overtimes, scheduled_overtime=scheduled_overtime, last_month_36_overtime=last_month_36_overtime, working_days=working_days)

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

        #31日分データ作成、ただし最終日でbreak
        for i in range(31):
            date = create_date + datetime.timedelta(days=i)
            overtime = [Overtime(
                status = 0,
                date = date,
                weekday = date.weekday(),
                time = 0,
                holiday_time = 0,
                total_time = 0,
                time_36 = 0,
                estimated_time = 0)] 
            db.session.add_all(overtime)
            if date == last_date:
                break
        db.session.commit()

        return redirect(url_for('index'))

@app.route('/new', methods=["POST"])
def new():
    overtime = Overtime()
    date = datetime.datetime.strptime(request.form["new_date"], '%Y-%m-%d') #型変換
    overtime.date = datetime.date(date.year, date.month, date.day) #年月日だけに変換
    overtime.weekday = date.weekday()
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
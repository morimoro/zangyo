#残業を管理するアプリ

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

name = "test"

class Overtime(db.Model):

    #データベースのテーブル名
    __tablename__ = name
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

with app.app_context():
        db.create_all()

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'GET':

         #データベースのデータ数
        date_count = Overtime.query.count()
        print(date_count)

        #月間予定残業に最終日の理想残業時間を代入
        #データがなければ初期値として0を代入
        try:
            overtime = db.session.query(Overtime).filter(Overtime.id==date_count).first()
            scheduled_overtime = overtime.estimated_time
        except:
            scheduled_overtime = 0
        
        #前月最終日36残業時間に36残業-残業時間を代入
        #データベースがなければ初期値として0を代入
        try:
            overtime = db.session.query(Overtime).filter(Overtime.id==1).first()
            last_month_36_overtime = overtime.time_36 - overtime.time
        except:
            last_month_36_overtime = 0
        
        #月間稼働日に初期値として0を代入
        working_days = 0

        #日付を昇順に並べ替え
        overtimes = Overtime.query.order_by(Overtime.date).all()
        db.session.commit()

        return render_template("index.html",
        overtimes = overtimes, scheduled_overtime=scheduled_overtime, last_month_36_overtime=last_month_36_overtime, working_days=working_days)

    else:
        print('update')

        #データベースのデータ数
        date_count = Overtime.query.count()
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
            overtime = db.session.query(Overtime).filter(Overtime.id==1).first()
            sum_36 = overtime.time_36 - overtime.time

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

        #出勤日をカウントして月間稼働日数とする
        working_days = db.session.query(Overtime).filter(Overtime.status==1).count()
        #毎日の平均残業時間 = 月間予定残業 / 月間稼働日数
        ave_estimated_time = scheduled_overtime / working_days
        sum_estimated_time = 0
        #出勤日の場合、理想残業時間に毎日の平均残業時間を加算
        for i in range(date_count):
            overtime = db.session.query(Overtime).filter(Overtime.id==(i+1)).first()
            if overtime.status == 1:
                overtime.estimated_time = sum_estimated_time + ave_estimated_time
                sum_estimated_time = overtime.estimated_time
            else:
                overtime.estimated_time = sum_estimated_time
        db.session.commit()

        #日付を昇順に並べ替え
        overtimes = Overtime.query.order_by(Overtime.date).all()
        db.session.commit()

        test =Overtime.query.all()
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





@app.route('/test', methods=["GET"])
def test():
    if request.method == 'GET':
            
        class Overtime(db.Model):

            #データベースのテーブル名
            __table_args__ = {'extend_existing': True}
            __tablename__ = "test2"
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

        with app.app_context():
                db.create_all()

        #データベースのデータ数
        date_count = Overtime.query.count()
        print(date_count)

        #月間予定残業に最終日の理想残業時間を代入
        #データがなければ初期値として0を代入
        try:
            overtime = db.session.query(Overtime).filter(Overtime.id==date_count).first()
            scheduled_overtime = overtime.estimated_time
        except:
            scheduled_overtime = 0
        
        #前月最終日36残業時間に36残業-残業時間を代入
        #データベースがなければ初期値として0を代入
        try:
            overtime = db.session.query(Overtime).filter(Overtime.id==1).first()
            last_month_36_overtime = overtime.time_36 - overtime.time
        except:
            last_month_36_overtime = 0
        
        #月間稼働日に初期値として0を代入
        working_days = 0

        #日付を昇順に並べ替え
        overtimes = Overtime.query.order_by(Overtime.date).all()
        db.session.commit()

        return render_template("index.html",
        overtimes = overtimes, scheduled_overtime=scheduled_overtime, last_month_36_overtime=last_month_36_overtime, working_days=working_days)

# @app.route('/new', methods=["POST"])
# def new():
#     overtime = Overtime()
#     date = datetime.datetime.strptime(request.form["new_date"], '%Y-%m-%d') #型変換
#     overtime.date = datetime.date(date.year, date.month, date.day) #年月日だけに変換
#     overtime.weekday = date.weekday()
#     overtime.time = float(request.form["new_text"])
#     totals = db.session.query(Overtime.time).all()
#     sum = 0
#     for total in totals:
#         sum = sum + total[0]
#     overtime.total_time = sum + overtime.time
#     overtime.status = 0
#     overtime.time_36 = 1
#     db.session.add(overtime)
#     db.session.commit()
#     return redirect(url_for('index'))

app.run(debug=True, host=os.getenv('APP_ADDRESS', 'localhost'), port=8001)
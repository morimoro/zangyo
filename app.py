#残業を管理するアプリ
#Flaskを動かす
# set FLASK_APP=app
# set FLASK_ENV=development
# flask run

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import desc #降順に並べ替えの時に必要
import os
import datetime

print("run")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///overtime.sqlite'

# データベースの作成
db = SQLAlchemy(app)

# ユーザー名とパスワードを記録するデータベース
class LoginUser(db.Model):

    __tablename__ = "login_user_name"
    #データベースの要素
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String())
    password = db.Column(db.String())

with app.app_context():
    db.create_all()

######################################################################################
#メインページ
@app.route('/', methods=["GET"])
def index():
    if request.method == 'GET':
        return render_template("index.html")

######################################################################################
#ユーザー名とパスワードを作成するページ
@app.route('/user_create', methods=["GET", "POST"])
def user():
    if request.method == 'GET':
        return render_template("user_create.html")

    else:
        user_name_input = request.form["user_name"]
        password_input = request.form["password"]

        user_data = [LoginUser(
            user_name = user_name_input,
            password = password_input)] 
        
        # LoginUserのデータベースにuser_name_inputが存在していれば、警告
        # 存在していない場合データベースにUser_nameとpasswordを追加
        try:
            exist = db.session.query(LoginUser).filter(LoginUser.user_name == user_name_input).first()
            exist.user_name
            flash('ユーザー名がすでに存在します')
            return render_template("user_create.html")

        except:
            db.session.add_all(user_data)
            db.session.commit()

        class OvertimeUser(db.Model):

            #データベースのテーブル名
            __table_args__ = {'extend_existing': True}
            __tablename__ = user_name_input
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

        return redirect(url_for('home', user_name=user_name_input))

######################################################################################
# ログインページ
@app.route('/user_login', methods=["GET", "POST"])
def user_login():
    if request.method == 'GET':
        return render_template("user_login.html")
    
    else:
        user_name_input = request.form["user_name"]
        password_input = request.form["password"]

        # LoginUserのデータベースにuser_name_inputが存在かつパスワードが一致していれば、homeへ遷移
        # 存在していないまたはパスワードが一致しない場合警告をだしてindex.htmlへ戻る
        try:
            exist = db.session.query(LoginUser).filter(LoginUser.user_name == user_name_input).first()
            if exist.password == password_input:
                print(exist.user_name)
                print(exist.password)
                return redirect(url_for('home', user_name=user_name_input))
            else:
                flash('パスワードが一致しません')
                return render_template("user_login.html")

        except:
            flash('ユーザー名が存在しません')
            return render_template("user_login.html")

######################################################################################
# ユーザー毎の残業確認ページ
@app.route('/home/<user_name>', methods=["GET", "POST"])
def home(user_name):
    if request.method == "GET":

        class OvertimeUser(db.Model):

            #データベースのテーブル名
            __table_args__ = {'extend_existing': True}
            __tablename__ = user_name
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

        #データベースのデータ数
        date_count = OvertimeUser.query.count()
        print(date_count)

        #月間予定残業に最終日の理想残業時間を代入
        #データがなければ初期値として0を代入
        try:
            overtime = db.session.query(OvertimeUser).filter(OvertimeUser.id==date_count).first()
            scheduled_overtime = overtime.estimated_time
        except:
            scheduled_overtime = 0
        
        #前月最終日36残業時間に36残業-残業時間を代入
        #データベースがなければ初期値として0を代入
        try:
            overtime = db.session.query(OvertimeUser).filter(OvertimeUser.id==1).first()
            last_month_36_overtime = overtime.time_36 - overtime.time
        except:
            last_month_36_overtime = 0
        
        #出勤日をカウントして月間稼働日数とする
        working_days = db.session.query(OvertimeUser).filter(OvertimeUser.status==1).count()

        #日付を昇順に並べ替え
        overtimes = OvertimeUser.query.order_by(OvertimeUser.date).all()
        db.session.commit()

        #残業時間をリスト化
        date_list = []
        total_time_list = []
        estimated_time_list = []
        time_36_list = []
        for i in range(date_count):
            overtime = db.session.query(OvertimeUser).filter(OvertimeUser.id==(i+1)).first()
            date_list.append(overtime.date)
            total_time_list.append(overtime.total_time)
            estimated_time_list.append(overtime.estimated_time)
            time_36_list.append(overtime.time_36)

        # 今日の日付を取得
        today = datetime.date.today()
        today = datetime.datetime.strftime(today, '%Y-%m-%d') #型変換

        return render_template("index_user.html",
        overtimes = overtimes, scheduled_overtime=scheduled_overtime, last_month_36_overtime=last_month_36_overtime, working_days=working_days,
        date_list=date_list, total_time_list=total_time_list, estimated_time_list=estimated_time_list, time_36_list=time_36_list,
        today=today, user_name=user_name)

    else:
        print('update')

        class OvertimeUser(db.Model):

            #データベースのテーブル名
            __table_args__ = {'extend_existing': True}
            __tablename__ = user_name
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

        #データベースのデータ数
        date_count = OvertimeUser.query.count()
        print(date_count)

        #月間予定残業を取得、未入力なら0を代入
        try:
            scheduled_overtime = float(request.form["scheduled_overtime"] or "0")
        except:
            scheduled_overtime = 0
        
        #前月最終日36残業時間を取得、未入力なら0を代入
        try:
            last_month_36_overtime = float(request.form["last_month_36_overtime"] or "0")
            sum_36 = last_month_36_overtime 
        except:
            last_month_36_overtime = 0
            overtime = db.session.query(OvertimeUser).filter(OvertimeUser.id==1).first()
            sum_36 = overtime.time_36 - overtime.time

        # データベースの回数だけ繰り返し、値を取得して月間残業、36残業を計算
        sum = 0
        for i in range(date_count):
            overtime = db.session.query(OvertimeUser).filter(OvertimeUser.id==(i+1)).first()
            overtime.status = int(request.form["status_{}".format(i+1)])
            overtime.time = float(request.form["time_{}".format(i+1)] or "0")
            overtime.holiday_time = float(request.form["holiday_time_{}".format(i+1)] or "0")
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
        working_days = db.session.query(OvertimeUser).filter(OvertimeUser.status==1).count()
        #毎日の平均残業時間 = 月間予定残業 / 月間稼働日数
        ave_estimated_time = scheduled_overtime / working_days
        sum_estimated_time = 0
        #出勤日の場合、理想残業時間に毎日の平均残業時間を加算
        for i in range(date_count):
            overtime = db.session.query(OvertimeUser).filter(OvertimeUser.id==(i+1)).first()
            if overtime.status == 1:
                overtime.estimated_time = sum_estimated_time + ave_estimated_time
                sum_estimated_time = overtime.estimated_time
            else:
                overtime.estimated_time = sum_estimated_time
        db.session.commit()

        #日付を昇順に並べ替え
        overtimes = OvertimeUser.query.order_by(OvertimeUser.date).all()
        db.session.commit()

        #残業時間をリスト化
        date_list = []
        total_time_list = []
        estimated_time_list = []
        time_36_list = []
        for i in range(date_count):
            overtime = db.session.query(OvertimeUser).filter(OvertimeUser.id==(i+1)).first()
            date_list.append(overtime.date)
            total_time_list.append(overtime.total_time)
            estimated_time_list.append(overtime.estimated_time)
            time_36_list.append(overtime.time_36)
        
        # 今日の日付を取得
        today = datetime.date.today()
        today = datetime.datetime.strftime(today, '%Y-%m-%d') #型変換

        return render_template("index_user.html",
        overtimes = overtimes, scheduled_overtime=scheduled_overtime, last_month_36_overtime=last_month_36_overtime, working_days=working_days,
        date_list=date_list, total_time_list=total_time_list, estimated_time_list=estimated_time_list, time_36_list=time_36_list,
        today=today, user_name=user_name)

######################################################################################
# 残業データ作成ページ
@app.route('/create/<user_name>', methods=["GET", "POST"])
def create_user(user_name):
    if request.method == 'GET':
        print('create')
        return render_template("create.html", user_name=user_name)
    else:
        print('create_date')
        create_date = request.form["create_date"] #create_dateを読み込み
        create_date = datetime.datetime.strptime(create_date, '%Y-%m-%d') #型変換
        create_date = datetime.date(create_date.year, create_date.month, create_date.day) #年月日だけに変換
        last_date = request.form["last_date"] #last_dateを読み込み
        last_date = datetime.datetime.strptime(last_date, '%Y-%m-%d') #型変換
        last_date = datetime.date(last_date.year, last_date.month, last_date.day) #年月日だけに変換
        print(create_date, last_date)

        class OvertimeUser(db.Model):

            #データベースのテーブル名
            __table_args__ = {'extend_existing': True}
            __tablename__ = user_name
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

        #31日分データ作成、ただし最終日でbreak
        for i in range(31):
            date = create_date + datetime.timedelta(days=i)
            if date.weekday() == 5 or date.weekday() ==6:
                overtime = [OvertimeUser(
                    status = 0,
                    date = date,
                    weekday = date.weekday(),
                    time = 0,
                    holiday_time = 0,
                    total_time = 0,
                    time_36 = 0,
                    estimated_time = 0)] 
            else :
                overtime = [OvertimeUser(
                    status = 1,
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

        return redirect(url_for('home', user_name=user_name))

########################################################################################
# 残業データすべて削除ページ
@app.route('/delete/<user_name>')
def delete_user(user_name):

    class OvertimeUser(db.Model):

            #データベースのテーブル名
            __table_args__ = {'extend_existing': True}
            __tablename__ = user_name
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

    # Overtimeデータベース削除
    OvertimeUser.query.delete()
    db.session.commit()
    return redirect(url_for('home', user_name=user_name))

# app.run(debug=True, host=os.getenv('APP_ADDRESS', 'localhost'), port=8001)
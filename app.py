from flask import Flask, render_template, request, redirect, url_for, session, g
from flask_sqlalchemy import SQLAlchemy
import config
from flask_bootstrap import Bootstrap
from functools import wraps
from datetime import datetime
from sqlalchemy import or_
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
app.config.from_object(config)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__='user'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    telephone = db.Column(db.String(11),nullable=False)
    username = db.Column(db.String(50),nullable=False)
    password = db.Column(db.String(100),nullable=False)
    # 拦截后更改保存数据，密码加密
    def __init__(self,*args,**kwargs):
        telephone = kwargs.get('telephone')
        username = kwargs.get('username')
        password = kwargs.get('password')

        self.telephone = telephone
        self.username = username
        self.password = generate_password_hash(password) #导入函数加密

    # 这是检查密码函数，传入密码与哈希加密后的密码相同返回true
    def check_password(self,raw_password):
        result = check_password_hash(self.password,raw_password)
        return result

class Question(db.Model):
    __tablename__='question'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    title = db.Column(db.String(100),nullable=False)
    content = db.Column(db.TEXT,nullable=False)
    # now()获取的是服务器第一次运行的时间，now就是每次创建一个模型的时候，都获取当前的时间
    create_time = db.Column(db.DateTime,default=datetime.now)
    author_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    author = db.relationship('User',backref=db.backref('questions'))

class Answer(db.Model):
    __tablename__ ='answer'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    content = db.Column(db.TEXT,nullable=False)
    create_time = db.Column(db.DateTime,default=datetime.now)
    question_id = db.Column(db.Integer,db.ForeignKey('question.id'))
    author_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    # 降序排序 id从大到小
    question = db.relationship('Question',backref = db.backref('answers',order_by=id.desc()))
    author = db.relationship('User',backref = db.backref('answers'))

db.create_all()

# 登录限制的装饰器
def login_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        # 如果登录状态，则可以执行访问
        if session.get('user_id'):
            return func(*args,**kwargs)
        else:
            # 否则直接跳转到登录页面
            return redirect(url_for('login'))
    return wrapper

@app.route('/')
def index():
    questions = Question.query.order_by('-create_time').all()
    return render_template('index.html',questions=questions)

@app.route('/detail/<question_id>')
def detail(question_id):
    question_model = Question.query.filter(Question.id==question_id).first()
    comment = Answer.query.filter(Answer.question_id==question_id).count()
    return render_template('detail.html',question=question_model,comment=comment)

@app.route('/add_answer',methods=['POST'])
@login_required
def add_answer():
    content = request.form.get('answer_content')
    question_id = request.form.get('question_id')
    answer = Answer(content=content)
    # 有两个外键，得知道这个评论的作者和这个问题
    question = Question.query.filter(Question.id==question_id).first()
    answer.author = g.user
    answer.question = question
    db.session.add(answer)
    db.session.commit()

    return redirect(url_for('detail',question_id=question_id))

@app.route('/login',methods = [ 'GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter(User.telephone==telephone).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return '手机号码或者密码错误，请确认后再登录'

@app.route('/regist',methods = [ 'GET','POST'])
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter(User.telephone == telephone).first()
        if user:
            return '该手机号已被注册'
        else:
            if password1 != password2:
                return '两次密码不相等，请核对后再填写'
            else:
                user = User(telephone=telephone,username=username,password=password1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # session.pop('user_id')
    # del session['user_id']
    session.clear()
    return redirect(url_for('login'))

@app.route('/question',methods = ['GET','POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        question = Question(title=title,content=content)
        # 因为有外键所以要指明是哪个作者author，所以从session里取出user_id找出user赋予question的作者
        question.author = g.user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/search')
def search():
    q = request.args.get('q')
    questions = Question.query.filter(or_(Question.title.contains(q),Question.content.contains(q)))
    return render_template('index.html',questions=questions)

@app.route('/admin/')
def admin():
    user = g.user
    return render_template('admin.html',user=user)

# 在视图函数钱执行的钩子函数
@app.before_request
def my_before_request():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id==user_id).first()
        if user:
            g.user = user


# 可以判断显示登录状态，不登录的状态一直执行
@app.context_processor
def my_context_processor():
    if hasattr(g,'user'):
        return {'user':g.user}
    return {}

if __name__ == '__main__':
    app.run()
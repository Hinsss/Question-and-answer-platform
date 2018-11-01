from datetime import timedelta
DEBUG = True
SECRET_KEY = "123456"
PERMANENT_SESSION_LIFETIME = timedelta(days=7)


HOSTNAME = '127.0.0.1'  # 主机名
PORT = 3306  # 端口号
DATABASE = 'wade'  # 数据库名称
USERNAME = 'root'  # 用户名
PASSWORD = '115113'  # 密码


#数据库SQLAlchemy，SQLALCHEMY_DATABASE_URI
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(
    USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
SQLALCHEMY_DATABASE_URI = DB_URI

SQLALCHEMY_TRACK_MODIFICATIONS = False

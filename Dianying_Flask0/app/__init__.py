#coding:utf-8
from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from flask.ext.redis import FlaskRedis
import pymysql
import os

app = Flask(__name__)
# 连接数据库
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost:3306/movie?charset=utf8"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['SECRET_KEY'] = '13066cc4f0d74ad59b56244b561c262e'      #跨站请求伪造
app.config["UP_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/")   #电影存放为相对路径
app.config["FC_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/users/")   #会员存放为相对路径
app.config["REDIS_URL"] = "redis://127.0.0.1:6379/0"

app.debug = True        #开启调试模式

# 实例化数据库
db = SQLAlchemy(app)
rd = FlaskRedis
#注册蓝图
from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint,url_prefix="/admin")

#404报错页面
@app.errorhandler(404)
def page_not_found(error):
    return render_template('home/404.html'), 404
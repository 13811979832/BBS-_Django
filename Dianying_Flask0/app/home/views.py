# coding:utf-8

from . import home
from flask import render_template, redirect, flash, url_for, session, request,Response
from app.home.forms import RegisterForm, LoginForm, UserdetailForm, PwdForm, CommentForm
from app.models import User, Userlog, Preview, Tag, Comment, Movie, Moviecol
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename  # 把filename转换成安全的名称,secure_filename不识别中文
from werkzeug.security import check_password_hash
from app import db, app, rd
import uuid, datetime
from functools import wraps
import os


# 设置装饰器，不登录不能访问主页
def user_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('home.login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)  # 把文件切割为后缀名+前缀
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


# 登录
@home.route("/login/", methods=["GET", "POST"])
def login():
    # 实例化表单
    form = LoginForm()
    # 数据库操作
    if form.validate_on_submit():  # 提交表单时进行验证
        # 获取输入的数据
        data = form.data

        # 判断输入的账号是否正确
        user_count = User.query.filter_by(name=data["name"]).count()  # 读取数据库里数据的个数
        if user_count == 0:
            flash("账号错误！", "err")
            return redirect(url_for("home.login"))

        # 数据库里筛选查找tag名是否有相同的
        user = User.query.filter_by(name=data["name"]).first()
        if not user.check_pwd(data['pwd']):  # 如果密码错误
            flash("密码错误！", "err")
            return redirect(url_for("home.login"))

        # 密码正确，就保存到session里
        session["user"] = data["name"]
        # 保存id,用于日志
        session["user_id"] = user.id

        userlog = Userlog(
            user_id=user.id,
            ip=request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()
        return redirect(url_for("home.user"))
    return render_template('home/login.html', form=form)


# 退出
@home.route("/logout/")
def logout():
    session.pop("user", None)
    session.pop("user_id", None)
    return redirect(url_for("home.login"))


# 注册会员
@home.route("/register/", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data
        user = User(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            pwd=generate_password_hash(data["pwd"]),
            uuid=uuid.uuid4().hex,
        )
        db.session.add(user)
        db.session.commit()
        flash("用户注册成功!", "ok")
    return render_template("home/register.html", form=form)


# 会员中心
@home.route("/user/", methods=["GET", "POST"])
@user_login_req
def user(id=None):
    form = UserdetailForm()
    user = User.query.get(session["user_id"])
    form.face.validators = []
    if request.method == "GET":
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
        form.info.data = user.info
    if form.validate_on_submit():
        data = form.data
        if form.face.data != "":
            file_face = secure_filename(form.face.data.filename)
            # 如果找不到存放的目录，就自动创建一个多级目录
            if not os.path.exists(app.config["FC_DIR"]):
                os.makedirs(app.config["FC_DIR"])  # 建文件夹
                os.chmod(app.config["FC_DIR"], "rw")  # 给文件授权，让可读可写
            user.face = change_filename(file_face)
            form.face.data.save(app.config["FC_DIR"] + user.face)  # 保存

        name_count = User.query.filter_by(name=data["name"]).count()
        if data["name"] != user.name and name_count == 1:
            flash("昵称已经存在", "err")
            return redirect(url_for("home.user"))

        email_count = User.query.filter_by(email=data["email"]).count()
        if data["email"] != user.email and email_count == 1:
            flash("邮箱已经存在", "err")
            return redirect(url_for("home.user"))

        phone_count = User.query.filter_by(phone=data["phone"]).count()
        if data["phone"] != user.phone and phone_count == 1:
            flash("手机号码已经存在", "err")
            return redirect(url_for("home.user"))

        user.name = data["name"]
        user.email = data["email"]
        user.phone = data["phone"]
        user.info = data["info"]
        db.session.add(user)
        db.session.commit()
        flash("修改成功", "ok")
        return redirect(url_for("home.user"))
    return render_template("home/user.html", form=form, user=user)


# 修改密码
@home.route("/pwd/", methods=["GET", "POST"])
@user_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=session["user"]).first()
        if not user.check_pwd(data["old_pwd"]):
            flash("旧密码错误！", "err")
            return redirect(url_for('home.pwd'))
        user.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(user)
        db.session.commit()
        flash("修改密码成功，请重新登录！", "ok")
        return redirect(url_for('home.logout'))
    return render_template("home/pwd.html", form=form)


# 会员登录日志
@home.route("/loginlog/<int:page>/", methods=["GET"])
@user_login_req
def loginlog(page=None):
    if page is None:
        page = 1
    page_data = Userlog.query.filter_by(
        user_id=int(session["user_id"])
    ).order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/loginlog.html", page_data=page_data)


# 主页
@home.route("/<int:page>/", methods=["GET"])  # 定义路由
def index(page=None):
    tags = Tag.query.all()
    page_data = Movie.query

    # 标签
    tid = request.args.get("tid", 0)
    if int(tid) != 0:
        page_data = page_data.filter_by(tag_id=int(tid))
    # 星级
    star = request.args.get("star", 0)
    if int(star) != 0:
        page_data = page_data.filter_by(star=int(star))
    # 上映时间
    time = request.args.get("time", 0)
    if int(time) != 0:
        # 根据电影添加时间降序
        if int(time) == 1:
            page_data = page_data.order_by(
                Movie.addtime.desc()
            )
        # 根据电影添加时间升序
        else:
            page_data = page_data.order_by(
                Movie.addtime.asc()
            )
    # 播放数量
    pm = request.args.get("pm", 0)
    # 根据电影播放量降序
    if int(pm) != 0:
        if int(pm) == 1:
            page_data = page_data.order_by(
                Movie.playnum.desc()
            )
        # 根据电影播放量升序
        else:
            page_data = page_data.order_by(
                Movie.playnum.asc()
            )
    # 评论数量
    cm = request.args.get("cm", 0)
    # 根据电影评论量降序
    if int(cm) != 0:
        if int(cm) == 1:
            page_data = page_data.order_by(
                Movie.commentnum.desc()
            )
        # 根据电影评论量升序
        else:
            page_data = page_data.order_by(
                Movie.commentnum.asc()
            )
    if page is None:
        page = 1
    page_data = page_data.paginate(page=page, per_page=10)
    p = dict(
        tid=tid,
        star=star,
        time=time,
        pm=pm,
        cm=cm,
    )
    return render_template('home/index.html', tags=tags, p=p, page_data=page_data)


# 轮播图,上映预告
@home.route("/animation/")  # 定义路由
def animation():
    data = Preview.query.all()
    return render_template('home/animation.html', data=data)


# 搜索
@home.route("/search/<int:page>/")  # 定义路由
def search(page=None):
    if page is None:
        page = 1
    key = request.args.get("key", "")
    page_data = Movie.query.filter(
        Movie.title.ilike('%' + key + '%')   #ilike模糊查询
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=10)
    page_data.key = key
    return render_template('home/search.html', page_data=page_data, key=key)


# 电影播放
@home.route("/play/<int:id>/<int:page>/", methods=["GET", "POST"])  # 定义路由
def play(id=None, page=None):
    # 电影播放
    movie = Movie.query.join(
        Tag
    ).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first_or_404()

    # 评论列表
    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == movie.id,
        User.id == Comment.user_id      #显示所有用户的评论信息
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page,per_page=10)
    # 播放量
    movie.playnum = movie.playnum + 1

    # 添加评论
    form = CommentForm()
    if "user" in session and form.validate_on_submit():
        data = form.data
        comment = Comment(
            content=data["content"],
            movie_id=movie.id,
            user_id=session["user_id"]
        )
        db.session.add(comment)
        db.session.commit()
        # 评论数量
        movie.commentnum = movie.commentnum + 1
        db.session.add(movie)
        db.session.commit()
        flash("评论成功", "ok")
        return redirect(url_for("home.play", id=movie.id, page=1))
    db.session.add(movie)
    db.session.commit()
    return render_template('home/play.html', movie=movie, form=form, page_data=page_data)


# 评论
@home.route("/comments/<int:page>/")
@user_login_req
def comments(page=None):
    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == session["user_id"]    #只显示用户自己的评论
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page,per_page=10)
    return render_template("home/comments.html",page_data=page_data)

#添加电影收藏
@home.route("/moviecol/add/")
@user_login_req
def moviecol_add():
    uid = request.args.get("uid","")
    mid = request.args.get("mid","")
    moviecol = Moviecol.query.filter_by(
        user_id = int(uid),
        movie_id = int(mid),
    ).count()
    if moviecol == 1:
        data = dict(ok=0)
    if moviecol == 0:
        moviecol = Moviecol(
            user_id=int(uid),
            movie_id=int(mid),
        )
        db.session.add(moviecol)
        db.session.commit()
        data = dict(ok=1)
    import json
    return json.dumps(data)

# 电影收藏列表
@home.route("/moviecol/<int:page>/")
@user_login_req
def moviecol(page=None):
    if page is None:
        page = 1
    page_data = Moviecol.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Moviecol.movie_id,
        User.id == session["user_id"]    #只显示用户自己的评论
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/moviecol.html",page_data=page_data)


#弹幕实例网址：http://dplayer.js.org/#/
@home.route("/video/<int:id>/<int:page>/", methods=["GET", "POST"])
def video(id=None, page=None):
    """
    弹幕播放器
    """
    movie = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first_or_404()

    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == movie.id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)

    movie.playnum = movie.playnum + 1
    form = CommentForm()
    if "user" in session and form.validate_on_submit():
        data = form.data
        comment = Comment(
            content=data["content"],
            movie_id=movie.id,
            user_id=session["user_id"]
        )
        db.session.add(comment)
        db.session.commit()
        movie.commentnum = movie.commentnum + 1
        db.session.add(movie)
        db.session.commit()
        flash("添加评论成功！", "ok")
        return redirect(url_for('home.video', id=movie.id, page=1))
    db.session.add(movie)
    db.session.commit()
    return render_template("home/video.html", movie=movie, form=form, page_data=page_data)


@home.route("/tm/", methods=["GET", "POST"])
def tm():
    """
    弹幕消息处理
    """
    import json
    if request.method == "GET":
        # 获取弹幕消息队列
        id = request.args.get('id')
        # 存放在redis队列中的键值
        key = "movie" + str(id)
        if rd.llen(key):
            msgs = rd.lrange(key, 0, 2999)
            res = {
                "code": 1,
                "danmaku": [json.loads(v) for v in msgs]
            }
        else:
            res = {
                "code": 1,
                "danmaku": []
            }
        resp = json.dumps(res)
    if request.method == "POST":
        # 添加弹幕
        data = json.loads(request.get_data())
        msg = {
            "__v": 0,
            "author": data["author"],
            "time": data["time"],
            "text": data["text"],
            "color": data["color"],
            "type": data['type'],
            "ip": request.remote_addr,
            "_id": datetime.datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex,
            "player": [
                data["player"]
            ]
        }
        res = {
            "code": 1,
            "data": msg
        }
        resp = json.dumps(res)
        # 将添加的弹幕推入redis的队列中
        rd.lpush("movie" + str(data["player"]), json.dumps(msg))
    return Response(resp, mimetype='application/json')

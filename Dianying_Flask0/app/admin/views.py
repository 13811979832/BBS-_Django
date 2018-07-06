# coding:utf-8
from . import admin
from flask import render_template, redirect, url_for, flash, session, request,abort
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm, PwdForm,AuthForm,RoleForm,AdminForm
from app.models import Admin, Tag, Movie, Preview, User, Comment, Moviecol, Oplog, Adminlog, Userlog,Auth,Role
from functools import wraps  # 定义装饰器
from app import db, app
from werkzeug.utils import secure_filename  # 把filename转换成安全的名称,secure_filename不识别中文
import os
import uuid  # 生成唯一字符串
import datetime


# 设置装饰器，不登录不能访问主页
def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function

# 权限控制装饰器
def admin_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin = Admin.query.join(
            Role
        ).filter(
            Role.id == Admin.role_id,
            Admin.id == session["admin_id"]
        ).first()
        auths = admin.role.auths
        auths = list(map(lambda v: int(v), auths.split(",")))
        auth_list = Auth.query.all()

        urls = [v.url for v in auth_list for val in auths if val == v.id]
        rule = request.url_rule

        if str(rule) not in urls:
            abort(404)      #返回抛出404错误信息
        return f(*args, **kwargs)

    return decorated_function


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)  # 把文件切割为后缀名+前缀
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


# 上下文应用处理器,映射到HTML页面里
@admin.context_processor
def tpl_extra():
    data = dict(
        # 当前时间
        online_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    return data


# 主页
@admin.route("/")  # 定义路由
@admin_login_req
def index():
    return render_template('admin/index.html')


# 登录
@admin.route("/login/", methods=["GET", "POST"])  # 定义路由
def login():
    # 实例化表单
    form = LoginForm()
    # 数据库操作
    if form.validate_on_submit():  # 提交表单时进行验证
        # 获取输入的数据
        data = form.data
        # 数据库里筛选查找tag名是否有相同的
        admin = Admin.query.filter_by(name=data['account']).first()
        if not admin.check_pwd(data['pwd']):  # 如果密码错误
            flash("密码错误！", "err")  # 提示
            return redirect(url_for('admin.login'))
        # 密码正确，就保存到session里
        session['admin'] = data['account']
        # 保存id,用于日志
        session["admin_id"] = admin.id

        # 管理员登录日志操作
        adminlog = Adminlog(
            admin_id=admin.id,
            ip=request.remote_addr,
        )
        db.session.add(adminlog)
        db.session.commit()

        return redirect(request.args.get('next') or url_for('admin.index'))
    return render_template('admin/login.html', form=form)


# 退出登录
@admin.route("/logout/")  # 定义路由
@admin_login_req
def logout():
    session.pop('admin', None)  # 点击退出，删除已存的session值
    session.pop("admin_id", None)
    return redirect(url_for('admin.login'))


# 修改密码
@admin.route("/pwd/", methods=["GET", "POST"])  # 定义路由
@admin_login_req
def pwd():
    form = PwdForm()
    # 提交表单时进行验证
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=session["admin"]).first()
        print(data["old_pwd"])
        from werkzeug.security import generate_password_hash
        admin.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(admin)
        db.session.commit()
        flash("密码修改成功，请重新登录！", "ok")
        return redirect(url_for("admin.logout"))
    return render_template('admin/pwd.html', form=form)


# 添加标签
@admin.route("/tag/add/", methods=["GET", "POST"])  # 定义路由
@admin_login_req
@admin_auth
def tag_add():
    form = TagForm()
    # 数据库操作
    if form.validate_on_submit():
        data = form.data
        # 数据库里筛选查找tag名是否有相同的
        tag = Tag.query.filter_by(name=data["name"]).count()
        # 如果有相同的
        if tag == 1:
            # 给提示
            flash("名称已经存在，请重新输入！", "err")
            # 跳转到该页
            return redirect(url_for("admin.tag_add"))
        # 数据库里没有相同的
        tag = Tag(
            name=data['name']
        )
        # 添加到数据库
        db.session.add(tag)
        # 提交
        db.session.commit()
        # 添加成功提示
        flash("标签添加成功！", "ok")

        # 标签日志操作
        oplog = Oplog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="添加标签%s" % data['name']
        )
        db.session.add(oplog)
        # 提交
        db.session.commit()

        # 调转到该页面
        redirect(url_for("admin.tag_add"))
    return render_template('admin/tag_add.html', form=form)


# 标签列表
@admin.route("/tag/list/<int:page>/", methods=['GET'])  # 定义路由
@admin_login_req
@admin_auth
def tag_list(page=None):
    if page is None:
        page = 1
    # 获取数据库的标签页的顺序
    page_data = Tag.query.order_by(
        # 按时间降序排序
        Tag.addtime.desc()
    ).paginate(page=page, per_page=10)  # per_page=5表示每页显示5条
    return render_template("admin/tag_list.html", page_data=page_data)


# 删除标签
@admin.route("/tag/del/<int:id>/", methods=['GET', 'POST'])  # 定义路由
@admin_login_req
@admin_auth
def tag_del(id=None):
    # 查询该id的标签，查不到就报404错误
    tag = Tag.query.filter_by(id=id).first_or_404()
    # 删除查到的标签
    db.session.delete(tag)
    # 确认删除
    db.session.commit()
    # 添加成功提示
    flash("标签删除成功！", "ok")
    # 调转到该页面
    return redirect(url_for("admin.tag_list", page=1))


# 编辑标签
@admin.route("/tag/edit/<int:id>/", methods=['GET', 'POST'])  # 定义路由
@admin_login_req
@admin_auth
def tag_edit(id=None):
    form = TagForm()
    tag = Tag.query.get_or_404(id)
    # 数据库操作
    if form.validate_on_submit():  # 提交表单时进行验证
        data = form.data
        # 数据库里筛选查找tag名是否有相同的
        tag_count = Tag.query.filter_by(name=data['name']).count()
        # 如果有相同的
        if tag.name != data['name'] and tag_count == 1:
            # 给提示
            flash("名称已经存在！", "err")
            # 跳转到该页
            return redirect(url_for("admin.tag_edit", id=id))
        # 替换原来的标签
        tag.name = data['name']
        # 添加到数据库
        db.session.add(tag)
        # 提交
        db.session.commit()
        # 添加成功提示
        flash("修改标签成功！", "ok")
        # 调转到该页面
        redirect(url_for("admin.tag_edit", id=id))
    return render_template('admin/tag_edit.html', form=form, tag=tag)


# 电影添加
@admin.route("/move/add/", methods=["GET", "POST"])  # 定义路由
@admin_login_req
@admin_auth
def movie_add():
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data

        movie_count = Movie.query.filter_by(title=data["title"]).count()
        if movie_count == 1:
            flash("片名已经存在", "err")
            return redirect(url_for("admin.movie_add", id=id))

        # 获取url的地址，secure_filename把filename转换成安全的名称
        file_url = secure_filename(form.url.data.filename)
        # 获取logo的地址
        file_logo = secure_filename(form.logo.data.filename)
        # 如果找不到存放电影的目录，就自动创建一个多级目录
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])  # 建文件夹
            os.chmod(app.config["UP_DIR"], "rw")  # 给文件授权，让可读可写
        url = change_filename(file_url)
        logo = change_filename(file_logo)
        form.url.data.save(app.config["UP_DIR"] + url)  # 保存
        form.logo.data.save(app.config["UP_DIR"] + logo)  # 保存

        movie = Movie(
            title=data['title'],
            url=url,
            info=data['info'],
            logo=logo,
            star=int(data['star']),
            playnum=0,
            commentnum=0,
            tag_id=int(data['tag_id']),
            area=data['area'],
            release_time=data['release_time'],
            length=data['length']
        )
        # 添加到数据库
        db.session.add(movie)
        # 提交
        db.session.commit()
        # 添加成功提示
        flash("电影添加成功！", "ok")
        # 调转到该页面
        redirect(url_for("admin.movie_add"))

    return render_template('admin/movie_add.html', form=form)


# 电影列表
@admin.route("/move/list/<int:page>", methods=["GET"])  # 定义路由
@admin_login_req
@admin_auth
def movie_list(page=None):
    if page is None:
        page = 1
    # 进行关联Tag的查询,单表查询使用filter_by 多表查询使用filter进行关联字段的声明
    # join用于关联tag
    page_data = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=5)
    return render_template("admin/movie_list.html", page_data=page_data)


# 编辑电影
@admin.route("/movie/edit/<int:id>/", methods=['GET', 'POST'])  # 定义路由
@admin_login_req
def movie_edit(id=None):
    form = MovieForm()
    form.url.validators = []
    form.logo.validators = []
    movie = Movie.query.get_or_404(int(id))
    # 编辑页面参数无法获得和数据库对应的值
    if request.method == "GET":
        form.info.data = movie.info
        form.tag_id.data = movie.tag_id
        form.star.data = movie.star
    # 数据库操作
    if form.validate_on_submit():  # 提交表单时进行验证
        # 可以修改的数据
        data = form.data
        movie_count = Movie.query.filter_by(title=data["title"]).count()
        if movie_count == 1:
            flash("片名已经存在", "err")
            return redirect(url_for("admin.movie_edit", id=id))

        # 如果找不到存放电影的目录，就自动创建一个多级目录
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])  # 建文件夹
            os.chmod(app.config["UP_DIR"], "rw")  # 给文件授权，让可读可写

        # 如果上传的视频不等于空，说明更改了文件
        if form.url.data != "":
            file_url = secure_filename(form.url.data.filename)  # 获取url的地址，secure_filename把filename转换成安全的名称
            movie.url = change_filename(file_url)
            form.url.data.save(app.config["UP_DIR"] + movie.url)  # 保存
        else:
            flash("上传的视频不能为空", "err")
            return redirect(url_for("admin.movie_edit", id=id))

        # 如果上传的图片不等于空，说明更改了文件
        if form.logo.data != "":
            file_logo = secure_filename(form.logo.data.filename)  # 获取logo的地址
            movie.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + movie.logo)  # 保存
        else:
            flash("上传的封面不能为空", "err")
            return redirect(url_for("admin.movie_edit", id=id))

        movie.star = data['star']
        movie.tag_id = data['tag_id']
        movie.info = data['info']
        movie.title = data['title']
        movie.area = data['area']
        movie.length = data['length']
        movie.release_time = data['release_time']
        db.session.add(movie)
        db.session.commit()
        flash("电影修改成功", "ok")
        return redirect(url_for("admin.movie_edit", id=movie.id))
    return render_template('admin/movie_edit.html', form=form, movie=movie)


# 电影删除
@admin.route("/movie/del/<int:id>", methods=["GET", "POST"])  # 定义路由
@admin_auth
def movie_del(id=None):
    # 数据库查找该电影的id，找不到就报错
    movie = Movie.query.get_or_404(int(id))
    db.session.delete(movie)
    db.session.commit()
    flash("电影删除成功", 'ok')
    return redirect(url_for("admin.movie_list", page=1))


# 上映预告添加
@admin.route("/preview/add/", methods=["GET", "POST"])
@admin_login_req
@admin_auth
def preview_add():
    form = PreviewForm()
    if form.validate_on_submit():
        # 获取输入的数据
        data = form.data
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], "rw")
        logo = change_filename(file_logo)
        form.logo.data.save(app.config["UP_DIR"] + logo)

        preview_count = Preview.query.filter_by(title=data["title"]).count()
        if preview_count == 1:
            flash("标题已经存在", "err")
            return redirect(url_for("admin.preview_add", id=id))

        preview = Preview(
            title=data["title"],
            logo=logo
        )

        db.session.add(preview)
        db.session.commit()
        flash("添加预告成功！", "ok")
        return redirect(url_for('admin.preview_add'))
    return render_template("admin/preview_add.html", form=form)


# 预告列表
@admin.route("/preview/list/<int:page>/", methods=['GET'])  # 定义路由
@admin_login_req
@admin_auth
def preview_list(page=None):
    form = Preview()
    if page is None:
        page = 1
    # 获取数据库的标签页的顺序
    page_data = Preview.query.order_by(
        # 按时间降序排序
        Preview.addtime.desc()
    ).paginate(page=page, per_page=10)  # per_page=5表示每页显示5条

    return render_template('admin/preview_list.html', page_data=page_data)


# 预告编辑
@admin.route("/preview/edit/<int:id>/", methods=['GET', 'POST'])  # 定义路由
@admin_login_req
@admin_auth
def preview_edit(id=None):
    form = PreviewForm()
    form.logo.validators = []
    preview = Preview.query.get_or_404(int(id))
    if request.method == "GET":
        form.title.data = preview.title
    if form.validate_on_submit():
        data = form.data

        if form.logo.data.filename != "":
            file_logo = secure_filename(form.logo.data.filename)
            preview.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + preview.logo)
        preview.title = data["title"]
        db.session.add(preview)
        db.session.commit()
        flash("修改预告成功", "ok")
        return redirect(url_for("admin.preview_edit", id=id))
    return render_template('admin/preview_edit.html', form=form, preview=preview)


# 预告删除
@admin.route("/preview/del/<int:id>/", methods=['GET', 'POST'])  # 定义路由
@admin_login_req
@admin_auth
def preview_del(id=None):
    preview = Preview.query.get_or_404(int(id))
    db.session.delete(preview)
    db.session.commit()
    flash("预告删除成功", "ok")
    return redirect(url_for("admin.preview_list", page=1))


# 会员列表
@admin.route("/user/list/<int:page>/", methods=["GET"])  # 定义路由
@admin_login_req
@admin_auth
def user_list(page=None):
    if page is None:
        pge = 1
    page_data = User.query.order_by(
        User.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/user_list.html', page_data=page_data)


# 会员查看
@admin.route("/user/view/<int:id>/", methods=["GET"])  # 定义路由
@admin_login_req
@admin_auth
def user_view(id=None):
    user = User.query.get_or_404(int(id))
    return render_template('admin/user_view.html', user=user)


# 会员删除
@admin.route("/user/del/<int:id>/", methods=["GET", "POST"])  # 定义路由
@admin_login_req
@admin_auth
def user_del(id=None):
    user = User.query.get_or_404(int(id))
    db.session.delete(user)
    db.session.commit()
    flash("会员删除成功", "ok")
    return redirect(url_for("admin.user_list", page=1))


# 评论列表
@admin.route("/comment/list/<int:page>/", methods=["GET"])  # 定义路由
@admin_login_req
@admin_auth
def comment_list(page=None):
    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/comment_list.html', page_data=page_data)


# 评论删除
@admin.route("/comment/del/<int:id>/", methods=["GET", "POST"])  # 定义路由
@admin_login_req
@admin_auth
def comment_del(id=None):
    comment = Comment.query.get_or_404(int(id))
    db.session.delete(comment)
    db.session.commit()
    flash("评论删除成功", "ok")
    return redirect(url_for("admin.comment_list", page=1))


# 收藏列表
@admin.route("/moviecol/list/<int:page>/", methods=["GET"])  # 定义路由
@admin_login_req
@admin_auth
def moviecol_list(page=None):
    if page is None:
        page = 1
    page_data = Moviecol.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Moviecol.movie_id,
        User.id == Moviecol.user_id
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/moviecol_list.html', page_data=page_data)


# 删除收藏列表id
@admin.route("/moviecol/del/<int:id>/", methods=["GET", "POST"])  # 定义路由
@admin_login_req
@admin_auth
def moviecol_del(id=None):
    moviecol = Moviecol.query.get_or_404(int(id))
    db.session.delete(moviecol)
    db.session.commit()
    flash("删除收藏成功", "ok")
    return redirect(url_for("admin.moviecol_list", page=1))


# 操作日志列表
@admin.route("/oplog/list/<int:page>/", methods=["GET"])  # 定义路由
@admin_login_req
@admin_auth
def oplog_list(page=None):
    if page is None:
        page = 1
    page_data = Oplog.query.join(
        Admin
    ).filter(
        Admin.id == Oplog.admin_id,
    ).order_by(
        Oplog.addtime.desc()
    ).paginate(page=page, per_page=10)

    return render_template('admin/oplog_list.html', page_data=page_data)


# 管理员登录日志列表
@admin.route("/adminloginlog/list/<int:page>/",methods=["GET"])  # 定义路由
@admin_login_req
@admin_auth
def adminloginlog_list(page=None):
    if page is None:
        page=1
    page_data = Adminlog.query.join(
        Admin
    ).filter(
        Admin.id == Adminlog.admin_id
    ).order_by(
        Adminlog.addtime.desc()
    ).paginate(page=page, per_page=10)

    return render_template('admin/adminloginlog_list.html',page_data=page_data)


# 会员登录日志列表
@admin.route("/userloginlog/list/<int:page>/",methods=["GET"])  # 定义路由
@admin_login_req
@admin_auth
def userloginlog_list(page=None):
    if page is None:
        page=1
    page_data = Userlog.query.join(
        User
    ).filter(
        User.id == Userlog.user_id
    ).order_by(
        Userlog.addtime.desc()
    ).paginate(page=page,per_page=10)
    return render_template('admin/userloginlog_list.html',page_data=page_data)


# 权限添加
@admin.route("/auth/add/",methods=["GET","POST"])  # 定义路由
@admin_login_req
@admin_auth
def auth_add():
    form = AuthForm()
    if form.validate_on_submit():
        data = form.data
        auth = Auth(
            name = data["name"],
            url = data["url"]
        )
        db.session.add(auth)
        db.session.commit()
        flash("添加权限成功","ok")
    return render_template('admin/auth_add.html',form=form)


# 权限列表
@admin.route("/auth/list/<int:page>/",methods=["GET"])  # 定义路由
@admin_login_req
@admin_auth
def auth_list(page=None):
    if page is None:
        page = 1
    page_data = Auth.query.order_by(
        Auth.addtime.desc()
    ).paginate(page=page,per_page=10)
    return render_template('admin/auth_list.html',page_data=page_data)

# 编辑权限
@admin.route("/auth/edit/<int:id>/",methods=["GET","POST"])  # 定义路由
@admin_login_req
@admin_auth
def auth_edit(id=None):
    form = AuthForm()
    auth = Auth.query.get_or_404(id)
    if form.validate_on_submit():
        data = form.data
        auth.name = data["name"]
        auth.url = data["url"]
        db.session.add(auth)
        db.session.commit()
        flash("修改权限成功","ok")
        redirect(url_for("admin.auth_edit",id=id))
    return render_template('admin/auth_edit.html',form=form,auth=auth)

# 权限删除
@admin.route("/auth/del/<int:id>/",methods=["GET","POST"])  # 定义路由
@admin_login_req
@admin_auth
def auth_del(id=None):
    auth = Auth.query.filter_by(id=id).first_or_404()
    db.session.delete(auth)
    db.session.commit()
    flash("权限删除成功","ok")
    return redirect(url_for("admin.auth_list", page=1))


# 角色添加
@admin.route("/role/add/",methods=["GET","POST"])  # 定义路由
@admin_login_req
@admin_auth
def role_add():
    form = RoleForm()
    if form.validate_on_submit():
        data = form.data
        role = Role(
            name = data["name"],
            auths = ",".join(map(lambda v:str(v),data["auths"]))
        )
        db.session.add(role)
        db.session.commit()
        flash("添加角色成功！","ok")
    return render_template('admin/role_add.html',form=form)


# 角色列表
@admin.route("/role/list/<int:page>/",methods=["GET"])  # 定义路由
@admin_login_req
@admin_auth
def role_list(page=None):
    if page is None:
        page = 1
    page_data = Role.query.order_by(
        Role.addtime.desc()
    ).paginate(page=page,per_page=10)
    return render_template('admin/role_list.html',page_data=page_data)

# 编辑角色
@admin.route("/role/edit/<int:id>/",methods=["GET","POST"])  # 定义路由
@admin_login_req
@admin_auth
def role_edit(id=None):
    form = RoleForm()
    role = Role.query.get_or_404(id)

    #默认选中标签
    if request.method == "GET":
        auths = role.auths
        # get时进行赋值。应对无法模板中赋初值
        form.auths.data = list(map(lambda v: int(v), auths.split(",")))
    if form.validate_on_submit():
        data = form.data
        role.name = data["name"]
        role.auths = ",".join(map(lambda v: str(v), data["auths"]))
        db.session.add(role)
        db.session.commit()
        flash("修改角色成功","ok")
        redirect(url_for("admin.role_edit",id=id))
    return render_template('admin/role_edit.html',form=form,role=role)

# 角色删除
@admin.route("/role/del/<int:id>/",methods=["GET","POST"])  # 定义路由
@admin_login_req
@admin_auth
def role_del(id=None):
    role = Role.query.filter_by(id=id).first_or_404()
    db.session.delete(role)
    db.session.commit()
    flash("角色删除成功","ok")
    return redirect(url_for("admin.role_list", page=1))


# 添加管理员
@admin.route("/admin/add/",methods=["GET","POST"])  # 定义路由
@admin_login_req
@admin_auth
def admin_add():
    form = AdminForm()
    from werkzeug.security import generate_password_hash
    if form.validate_on_submit():
        data = form.data
        admin = Admin(
            name = data["name"],
            pwd = generate_password_hash(data["pwd"]),
            role_id = data["role_id"],
            is_super = 1
        )
        db.session.add(admin)
        db.session.commit()
        flash("管理员添加成功！","ok")
    return render_template('admin/admin_add.html',form=form)


# 管理员列表
@admin.route("/admin/list/<int:page>/",methods=["GET"])  # 定义路由
@admin_login_req
@admin_auth
def admin_list(page=None):
    if page is None:
        page = 1
    page_data = Admin.query.join(
        Role
    ).filter(
        Role.id == Admin.role_id
    ).order_by(
        Admin.addtime.desc()
    ).paginate(page=page,per_page=10)
    return render_template('admin/admin_list.html',page_data=page_data)

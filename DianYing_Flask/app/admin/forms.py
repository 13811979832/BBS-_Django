# coding:utf-8

from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField, SubmitField, FileField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import Admin, Tag, Auth, Role

tags = Tag.query.all()
auth_list = Auth.query.all()
role_list = Role.query.all()


# 登录
class LoginForm(FlaskForm):
    """管理员登录表单"""
    # 账号
    account = StringField(
        label="账号",
        # 账号验证
        validators=[
            # 输入框为空时，提示
            DataRequired("请输入正确的账号！")
        ],
        # 描述
        description="账号",
        # html标签
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号",
            # "required": "required"  # 必须输入
        }

    )
    # 密码框
    pwd = PasswordField(
        label="密码",
        # 账号验证
        validators=[
            DataRequired("请输入正确密码！")
        ],
        # 描述
        description="密码",
        # html标签
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码",
            # "required": "required"  # 必须输入
        }
    )
    submit = SubmitField(
        label="登录",
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }
    )

    # 验证账号是否正确
    def validate_account(self, field):
        account = field.data
        admin = Admin.query.filter_by(name=account).count()  # 读取数据库里数据的个数
        if admin == 0:
            raise ValidationError("账号不存在！")


# 标签
class TagForm(FlaskForm):
    name = StringField(
        label="名称",
        # 验证
        validators=[
            DataRequired("请输入标签!")
        ],
        # 描述
        description="标签",
        # HTML标签
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入标签名称！"
        }
    )
    submit = SubmitField(
        label="提交",
        render_kw={
            "class": "btn btn-primary",
        }
    )


# 创建电影
class MovieForm(FlaskForm):
    # 标题
    title = StringField(
        label="片名",
        # 验证
        validators=[
            DataRequired("片名不能为空!")
        ],
        # 描述
        description="片名",
        # HTML标签
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "请输入片名！"
        }
    )
    # 文件
    url = FileField(
        label="文件",
        # 验证
        validators=[
            DataRequired("请上传文件!")
        ],
        # 描述
        description="文件"
    )
    # 简介
    info = TextAreaField(
        label="介绍",
        # 验证
        validators=[
            DataRequired("简介不能为空!")
        ],
        # 描述
        description="介绍",
        # HTML标签
        render_kw={
            "class": "form-control",
            "rows": 10
        }
    )
    # 封面
    logo = FileField(
        label="封面",
        # 验证
        validators=[
            DataRequired("请上传封面!")
        ],
        # 描述
        description="封面",
    )
    # 星级
    star = SelectField(
        label="星级",
        # 验证
        validators=[
            DataRequired("请选择星级!")
        ],
        coerce=int,
        choices=[(1, "1星"), (2, "2星"), (3, "3星"), (4, "4星"), (5, "5星")],
        # 描述
        description="星级",
        render_kw={
            "class": "form-control",
        }
    )
    # 所属标签
    tag_id = SelectField(
        label="标签",
        # 验证
        validators=[
            DataRequired("请选择标签!")
        ],
        coerce=int,
        choices=[(v.id, v.name) for v in tags],
        # 描述
        description="标签",
        render_kw={
            "class": "form-control",
        }
    )
    # 上映地区
    area = StringField(
        label="地区",
        # 验证
        validators=[
            DataRequired("请输入地区!")
        ],
        # 描述
        description="地区",
        # HTML标签
        render_kw={
            "class": "form-control",
            "placeholder": "请输入地区！"
        }
    )
    # 片长
    length = StringField(
        label="片长",
        # 验证
        validators=[
            DataRequired("请输入片长!")
        ],
        # 描述
        description="片长",
        # HTML标签
        render_kw={
            "class": "form-control",
            "id": "input_length",
            "placeholder": "请输入片长！"
        }
    )
    # 上映时间
    release_time = StringField(
        label="上映时间",
        # 验证
        validators=[
            DataRequired("请输入上映时间!")
        ],
        # 描述
        description="上映时间",
        # HTML标签
        render_kw={
            "class": "form-control",
            "id": "input_release_time",
            "placeholder": "请输入上映时间！"
        }
    )
    submit = SubmitField(
        label="添加",
        render_kw={
            "class": "btn btn-primary",
        }
    )


# 上映预告
class PreviewForm(FlaskForm):
    # 标题
    title = StringField(
        label="预告标题",
        # 验证
        validators=[
            DataRequired("预告标题不能为空!")
        ],
        # 描述
        description="预告标题",
        # HTML标签
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "请输入预告标题！"
        }
    )
    # 封面
    logo = FileField(
        label="预告封面",
        # 验证
        validators=[
            DataRequired("请上传预告封面!")
        ],
        # 描述
        description="预告封面",
    )
    submit = SubmitField(
        label="添加",
        render_kw={
            "class": "btn btn-primary",
        }
    )


# 修改密码
class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label="旧密码",
        validators=[
            DataRequired("请输入你的旧密码！")
        ],
        render_kw={
            "class": "form-control",
            "id": "input_pwd",
            "placeholder": "请输入旧密码！"
        }
    )

    new_pwd = PasswordField(
        label="新密码",
        validators=[
            # 输入框为空时，提示
            DataRequired("请输入你的新密码！")
        ],
        render_kw={
            "class": "form-control",
            "id": "input_newpwd",
            "placeholder": "请输入新密码！"
        }
    )

    submit = SubmitField(
        label="修改",
        render_kw={
            "class": "btn btn-primary",
        }
    )

    # 验证旧密码是否正确
    def validate_old_pwd(self, field):
        from flask import session
        # 获取输入的旧密码
        pwd = field.data
        name = session['admin']
        admin = Admin.query.filter_by(
            name=name
        ).first()
        # 验证数据库密码和输入的密码是否相同,不相同，提示错误
        if not admin.check_pwd(pwd):
            raise ValidationError("旧密码错误，请重新输入！")


# 添加权限
class AuthForm(FlaskForm):
    name = StringField(
        label="权限名称",
        # 验证
        validators=[
            DataRequired("权限名称不能为空!")
        ],
        # 描述
        description="权限名称",
        # HTML标签
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入权限名称！"
        }
    )

    url = StringField(
        label="权限地址",
        # 验证
        validators=[
            DataRequired("权限地址不能为空!")
        ],
        # 描述
        description="权限地址",
        render_kw={
            "class": "form-control",
            "id": "input_url",
            "placeholder": "请输入权限地址！"
        }
    )
    submit = SubmitField(
        label="添加",
        render_kw={
            "class": "btn btn-primary",
        }
    )


# 添加角色
class RoleForm(FlaskForm):
    name = StringField(
        label="角色名称",
        # 验证
        validators=[
            DataRequired("角色名称不能为空!")
        ],
        # 描述
        description="角色名称",
        # HTML标签
        render_kw={
            "class": "form-control",
            "id": "role_name",
            "placeholder": "请输入角色名称！"
        }
    )

    auths = SelectMultipleField(
        label="权限列表",
        # 验证
        validators=[
            DataRequired("权限不能为空!")
        ],

        coerce=int,
        choices=[(v.id, v.name) for v in auth_list],
        # 描述
        description="权限列表",
        render_kw={
            "class": "form-control",
        }
    )
    submit = SubmitField(
        label="添加",
        render_kw={
            "class": "btn btn-primary",
        }
    )


# 添加管理员
class AdminForm(FlaskForm):
    name = StringField(
        label = "管理员名称",
        # 验证
        validators=[
            DataRequired("管理员名称不能为空!")
        ],
        # 描述
        description="管理员名称",
        # HTML标签
        render_kw={
            "class": "form-control",
            "id": "admin_name",
            "placeholder": "请输入管理员名称！"
        }
    )

    pwd = PasswordField(
        label="管理员密码",
        # 验证
        validators=[
            DataRequired("密码不能为空!")
        ],
        description="管理员密码",
        render_kw={
            "class": "form-control",
            "id": "admin_pwd",
            "placeholder": "请输入管理员密码！"
        }
    )
    re_pwd = PasswordField(
        label="管理员重复密码",
        # 验证
        validators=[
            DataRequired("重复密码不能为空!"),
            EqualTo("pwd", message="新密码与旧密码不一致！")
        ],
        description="管理员重复密码",
        render_kw={
            "class": "form-control",
            "id": "admin_repwd",
            "placeholder": "请输入管理员重复密码！"
        }
    )
    role_id = SelectField(
        label="所属角色",
        # 验证
        validators=[
            DataRequired("请选择所属角色!")
        ],
        coerce=int,
        choices=[(v.id, v.name) for v in role_list],
        description="所属角色",
        render_kw={
            "class": "form-control",
            "id": "input_role_id",

        }
    )
    submit = SubmitField(
        label="添加",
        render_kw={
            "class": "btn btn-primary",
        }
    )

#coding:utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email, Regexp
from app.models import Admin, Tag, Auth, Role,User

#会员注册
class RegisterForm(FlaskForm):
    name = StringField(
        label="昵称",
        # 账号验证
        validators=[
            # 输入框为空时，提示
            DataRequired("请输入昵称！")
        ],
        # 描述
        description="昵称",
        # html标签
        render_kw={
            "class": "form-control input-lg",
            "id": "input_name",
            "placeholder": "昵称",
        }
    )
    email = StringField(
        label="邮箱",
        # 账号验证
        validators=[
            # 输入框为空时，提示
            DataRequired("请输入邮箱！"),
            Email("邮箱格式不正确")
        ],
        # 描述
        description="邮箱",
        # html标签
        render_kw={
            "class": "form-control input-lg",
            "id": "input_email",
            "placeholder": "邮箱",
        }
    )
    phone = StringField(
        label="手机",
        # 账号验证
        validators=[
            # 输入框为空时，提示
            DataRequired("请输入手机号！"),
            Regexp("1[3458]\\d{9}",message="手机号码格式错误")    #正则表达式
        ],
        # 描述
        description="手机",
        # html标签
        render_kw={
            "class": "form-control input-lg",
            "id": "input_phone",
            "placeholder": "手机",
        }
    )
    # 密码框
    pwd = PasswordField(
        label="密码",
        # 账号验证
        validators=[
            DataRequired("请输入密码！"),
        ],
        # 描述
        description="密码",
        # html标签
        render_kw={
            "class": "form-control input-lg",
            "id": "input_password",
            "placeholder": "密码",
            # "required": "required"  # 必须输入
        }
    )
    repwd = PasswordField(
        label="确认密码",
        # 账号验证
        validators=[
            DataRequired("请确认密码！"),
            EqualTo('pwd', message="两次密码不一致")
        ],
        # 描述
        description="确认密码",
        # html标签
        render_kw={
            "class": "form-control input-lg",
            "id": "input_repassword",
            "placeholder": "确认密码",
            # "required": "required"  # 必须输入
        }
    )
    submit = SubmitField(
        label="注册",
        render_kw={
            "class": "btn btn-lg btn-success btn-block",
        }
    )
    def validate_name(self,field):
        name = field.data
        user = User.query.filter_by(name=name).count()
        if user == 1:
            raise ValidationError("昵称已经存在")
    def validate_email(self,field):
        email = field.data
        user = User.query.filter_by(email=email).count()
        if user == 1:
            raise ValidationError("邮箱已经存在")
    def validate_phone(self,field):
        phone = field.data
        user = User.query.filter_by(phone=phone).count()
        if user == 1:
            raise ValidationError("手机号码已经存在")

#会员登录
class LoginForm(FlaskForm):
    """管理员登录表单"""
    # 账号
    name = StringField(
        label="账号",
        # 账号验证
        validators=[
            # 输入框为空时，提示
            DataRequired("账号不能为空！")
        ],
        # 描述
        description="账号",
        # html标签
        render_kw={
            "class": "form-control input-lg",
            "id": "input_contact",
            "placeholder": "用户名",
            # "required": "required"  # 必须输入
        }

    )
    # 密码框
    pwd = PasswordField(
        label="密码",
        # 账号验证
        validators=[
            DataRequired("密码不能为空！")
        ],
        # 描述
        description="密码",
        # html标签
        render_kw={
            "class": "form-control input-lg",
             "id": "input_password",
            "placeholder": "密码",
            # "required": "required"  # 必须输入
        }
    )
    submit = SubmitField(
        label="登录",
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }
    )

    # # 验证账号是否正确
    # def validate_user(self, field):
    #     name = field.data
    #     user = User.query.filter_by(name=name).count()  # 读取数据库里数据的个数
    #     if user == 0:
    #         raise ValidationError("账号不存在！")

#会员
class UserdetailForm(FlaskForm):
    name = StringField(
        label="昵称",
        # 账号验证
        validators=[
            # 输入框为空时，提示
            DataRequired("昵称不能为空！")
        ],
        # 描述
        description="昵称",
        # html标签
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "昵称",
            # "required": "required"  # 必须输入
        }

    )
    email = StringField(
        label="邮箱",
        # 账号验证
        validators=[
            # 输入框为空时，提示
            DataRequired("请输入邮箱！"),
            Email("邮箱格式不正确")
        ],
        # 描述
        description="邮箱",
        # html标签
        render_kw={
            "class": "form-control",
            "id": "input_email",
            "placeholder": "邮箱",
        }
    )
    phone = StringField(
        label="手机",
        # 账号验证
        validators=[
            # 输入框为空时，提示
            DataRequired("请输入手机号！"),
            Regexp("1[3458]\\d{9}", message="手机号码格式错误")  # 正则表达式
        ],
        # 描述
        description="手机",
        # html标签
        render_kw={
            "class": "form-control",
            "id": "input_phone",
            "placeholder": "手机",
        }
    )
    face = FileField(
        label="头像",
        # 验证
        validators=[
            DataRequired("上传头像!")
        ],
        # 描述
        description="头像",
    )
    info = TextAreaField(
        label="简介",
        # 账号验证
        validators=[
            # 输入框为空时，提示
            DataRequired("请输入简介！"),
        ],
        # 描述
        description="简介",
        # html标签
        render_kw={
            "class": "form-control",
            "id": "input_info",
            "rows":"10",
        }
    )
    submit = SubmitField(
        '保存修改',
        render_kw={
            "class": "btn btn-success",
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
            "id": "input_oldpwd",
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
        label="修改密码",
        render_kw={
            "class": "btn btn-success",
        }
    )

class CommentForm(FlaskForm):
    content = TextAreaField(
        label="内容",
        validators=[
            # 输入框为空时，提示
            DataRequired("请输入你的评论内容！")
        ],
        description="内容",
        render_kw={
            "id": "input_content",
        }
    )

    submit = SubmitField(
        label="提交评论",
        render_kw={
            "class": "btn btn-danger",
            "id": "btn-sub"
        }
    )
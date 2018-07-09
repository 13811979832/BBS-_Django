# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.test import TestCase
from app01.models import *
from django.test import Client
from django.contrib.auth.models import User

# Create your tests here.
'''
class ModelTest(TestCase):
    def setUp(self):
        # Admin.objects.create(username='lijie',password='123098',email='lijie@163.com',user_type=2)
        # Chat.objects.create(content='yiuifu',user_id=2)
        print '开始测试'

    def test_event_models(self):
        result = Admin.objects.get(username="alex")
        self.assertEqual(result.email, "123@163.com")
        self.assertEqual(result.password, '1234')

    def test_guest_models(self):
        result = Chat.objects.get(content='你是谁')
        self.assertEqual(result.user_id, 1)
'''
class LoginActionTest(TestCase):
    ''' 测试登录函数'''
    def setUp(self):
        User.objects.create_user('admin','admin123456', 'admin@mail.com')
        self.c = Client()

    def test_login_action_username_password_null(self):
        ''' 用户名密码为空 '''
        test_data = {'username':'','password':''}
        response = self.c.post('/app01/login/', data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("username or password error!", response.content)

    def test_login_action_username_password_error(self):
        '''用户名密码错误'''
        test_data = {'username': 'alex', 'password': '12345'}
        response = self.c.post('/app01/login/', data=test_data)
        self.assertEqual(response.status_code, 200)
        print response.content
        self.assertIn("username or password error!", response.content)

    def test_login_action_success(self):
        ''' 登录成功 '''
        test_data = {'username': 'admin', 'password': 'admin123456'}
        response = self.c.post('/app01/login/', data=test_data)
        self.assertEqual(response.status_code, 200)
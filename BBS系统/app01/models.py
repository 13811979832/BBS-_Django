# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class UserType(models.Model):

    display = models.CharField(max_length=50)

    def __unicode__(self):
        return self.display

class Admin(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=256)
    email = models.EmailField()
    user_type = models.ForeignKey('UserType')

    def __unicode__(self):
        return self.username

#聊天室
class Chat(models.Model):
    #聊天内容
    content = models.TextField()
    #发布者
    user = models.ForeignKey('Admin')
    #创建时间
    create_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.content

class NewsType(models.Model):
    display = models.CharField(max_length=50)

    def __unicode__(self):
        return self.display

class News(models.Model):
    title = models.CharField(max_length=30)
    #简要，概要
    summary = models.CharField(max_length=256)
    url = models.URLField()
    #点赞个数
    favor_count = models.IntegerField(default=0)
    #回复个数
    reply_count = models.IntegerField(default=0)
    news_type = models.ForeignKey('NewsType')
    #发布人
    user = models.ForeignKey('Admin')
    create_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title

#回复信息
class Reply(models.Model):
    #回复的内容
    content = models.TextField()
    #回复人
    user = models.ForeignKey('Admin')
    #回复的哪个新闻
    new = models.ForeignKey('News')
    #回复时间
    create_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.content








































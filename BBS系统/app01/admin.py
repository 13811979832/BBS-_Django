# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import UserType, Admin, Chat, NewsType, News, Reply

# Register your models here.
# admin.site.register([UserType, Admin, Chat, NewsType, News, Reply])

class UserTypeAdmin(admin.ModelAdmin):
    list_display = ['id','display']
    search_fields = ['display']    #搜索栏

class admin_Admin(admin.ModelAdmin):
    list_display = ['id','username','password','email','user_type']
    search_fields = ['username']
    list_filter = ['user_type']    #过滤器

class ChatAdmin(admin.ModelAdmin):
    list_display = ['id','user','content','create_date']
    search_fields = ['username']

class NewsTypeAdmin(admin.ModelAdmin):
    list_display = ['id','display']
    search_fields = ['display']

class NewsAdmin(admin.ModelAdmin):
    list_display = ['id','title','summary','url','favor_count','reply_count','news_type','user','create_date']
    search_fields = ['title','url','summary']
    list_filter = ['news_type','user']  # 过滤器

class ReplyAdmin(admin.ModelAdmin):
    list_display = ['id','content','user','new','create_date']
    list_filter = ['user']  # 过滤器

admin.site.register(UserType,UserTypeAdmin)
admin.site.register(Admin,admin_Admin)
admin.site.register(Chat,ChatAdmin)
admin.site.register(NewsType,NewsTypeAdmin)
admin.site.register(News,NewsAdmin)
admin.site.register(Reply,ReplyAdmin)
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, render_to_response,HttpResponse,redirect
from django.core import serializers
from app01 import models
import json
import datetime
from datetime import date
# Create your views here.
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)

        try:
            currentObj = models.Admin.objects.get(username=username,
                                                 password=password)
        except Exception,e:
            currentObj = None

        if currentObj:
            request.session['current_user_id'] = currentObj.id
            return redirect('/app01/index/')
        else:
            return render_to_response('login.html',{'error':'username or password error!'})

    return render_to_response('login.html',)



def Index(request):
    all_data = models.News.objects.all()
    rel = {'data':all_data}
    return render_to_response('index.html',rel)

def addfavor(request):
    ret = {'status':0,'data':'','message':''}
    try:
        id = request.POST.get('nid')
        newsObj = models.News.objects.get(id=id)
        temp = newsObj.favor_count + 1
        newsObj.favor_count = temp
        newsObj.save()
        ret['status'] = 1
        ret['data'] = temp
    except Exception,e:
        ret['message'] = e.message
    return HttpResponse(json.dumps(ret))

class CJsonEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

def getreply(request):
    id = request.POST.get('nid')
    reply_list = models.Reply.objects.filter(new__id=id).values('id','content','create_date','user__username')
    print type(reply_list)
    reply_list = list(reply_list)
    print type(reply_list)
    reply_list = json.dumps(reply_list,cls=CJsonEncoder)
    #reply_list = serializers.serialize("json",reply_list)
    print reply_list
    return HttpResponse(reply_list)

def submitreply(request):
    ret = {'status': 0, 'data': '', 'message': ''}
    try:
        nid = request.POST.get('nid')
        data = request.POST.get('data')
        newsobj = models.News.objects.get(id=nid)
        print request.POST.get('nid')
        print request.POST.get('data')
        #网数据库里添加数据
        obj = models.Reply.objects.create(content=data,
                                    user=models.Admin.objects.get(id=request.session['current_user_id']),
                                    new=newsobj)
        temp = newsobj.reply_count + 1
        newsobj.reply_count = temp
        newsobj.save()
        ret['data'] = {'reply_count':temp,
                       'content':obj.content,
                       'user__username':obj.user.username,
                       'create_date':obj.create_date.strftime('%Y-%m-%d %H:%M:%S')}
        ret['status'] = 1
    except Exception,e:
        ret['message'] = e.message

    return HttpResponse(json.dumps(ret))



def submitchat(request):
    ret = {'status': 0, 'data': '', 'message': ''}
    try:
        value = request.POST.get("data")
        obj = models.Chat.objects.create(content=value,
                                            user=models.Admin.objects.get(id=request.session['current_user_id']))

        ret['status'] = 1
        ret['data'] = {'id':obj.id,
                       'username':obj.user.username,
                       'create_date':obj.create_date.strftime('%Y-%m-%d %H:%M:%S')}
    except Exception,e:
        ret['message'] = e.message

    return HttpResponse(json.dumps(ret))

#获取数据库里聊天记录最新10条，加载的聊天页面
def getchart(request):
    #倒序取值
    chatlist = models.Chat.objects.all().order_by('-id')[0:10].values('id','content','user__username','create_date')
    list_id = chatlist[0]['id']
    print list_id
    chatlist = list(chatlist)
    chatlist = json.dumps(chatlist, cls=CJsonEncoder)
    return HttpResponse(chatlist)

def getchart2(request):
    last_id = request.POST.get('lastid')
    chatlist = models.Chat.objects.filter(id__gt=last_id).values('id','content','user__username','create_date')
    chatlist = list(chatlist)
    chatlist = json.dumps(chatlist, cls=CJsonEncoder)
    return HttpResponse(chatlist)



























from django.conf.urls import url
from django.contrib import admin
from app01.views import Index,addfavor, getreply, submitreply,login,submitchat,getchart,getchart2

urlpatterns = [
    url(r'^login/', login),
    url(r'^index/', Index),
    url(r'^addfavor/', addfavor),
    url(r'^getreply/', getreply),
    url(r'^submitreply/', submitreply),
    url(r'^submitchat/', submitchat),
    url(r'^getchart/', getchart),
    url(r'^getchart2/', getchart2),
]

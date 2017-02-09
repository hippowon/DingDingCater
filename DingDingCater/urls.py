# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from DingDingCater import settings
import django.views.static as ds
from blog.views import page_index, page_article, page_category, ajax_praiseCnt, upload_image

urlpatterns = [
    # static file router
    # after inserting pic in kindeditor, kindeditor will request pic through this url.
    url(r"^uploads/(?P<path>.*)$", ds.serve, {"document_root": settings.MEDIA_ROOT, }),

    # kindeditor uploads pic to this url
    # get named group 'dir_name'，pass to upload_image()
    # here 'admin/uploads/' must be same to 'uploadJson' value defined in /static/js/kindeditor-4.1.11-en/config.js
    url(r'admin/uploads/(?P<dirNameUnderUpload>[^/]+)', upload_image),

    url(r'^category/$', page_category),

    url(r'^uploadPraise/$', ajax_praiseCnt),

    url(r'^article/$', page_article, name='article'), # ——> {% url 'article' %}

    url(r'^$', page_index),

    url(r'^admin/', include(admin.site.urls)),
]

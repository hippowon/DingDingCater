# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.admin import admin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from DingDingCater import settings

#get page of pageNum (start with 1)
def getPageFromArticles(article_list, pageNum):
    return Paginator(article_list, settings.ARTICLES_PERPAGE).page(pageNum)

class CAuthor(AbstractUser):
    # path start from 'MEDIA_URL' in settings.py
    headshot = models.ImageField(verbose_name='headshot',default='headshot/defaultHeadshot.png', upload_to='headshot/', max_length=350, blank=True,null=True)

    class Meta:
        verbose_name = 'Author'
        verbose_name_plural = verbose_name
        ordering = ['-id'] # reverse order of 'id'

    def __str__(self):
        return self.username

# top category and it's manager
class CTopCategoryManager(admin.ModelAdmin):
    list_editable = ["id"]
    list_display = ["name", "id"]
    ordering = ["id"]

class CTopCategory(models.Model):
    name = models.CharField(verbose_name='top category', default="default", max_length=40)

    class Meta:
        verbose_name = 'top category'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.name

# sub category and it's manager
class CCategoryManager(admin.ModelAdmin):
    list_editable = ["topCategoryId", "id"]
    list_display =["name", "topCategoryId", "id"]
    ordering = ["topCategoryId", "id"]

class CCategory(models.Model):
    name = models.CharField(verbose_name='sub category', default="default", max_length=40)
    topCategoryId = models.ForeignKey(CTopCategory, verbose_name='top category', null=True, blank=True)

    class Meta:
        verbose_name = 'sub category'
        verbose_name_plural = verbose_name
        ordering = ['topCategoryId', 'id']

    def __str__(self):
        return self.name

class CArticleManager(admin.ModelAdmin):
    # these fields will be shown in the admin page
    list_display =["title", "topCategoryId", "subCategoryId", "priority", "datePublish", "clickCnt", "praiseCnt"]
    list_per_page = 20
    list_editable = ["topCategoryId","subCategoryId","priority"]
    # you can filter articles by these fields in the admin page
    list_filter = ["datePublish","topCategoryId","subCategoryId"]
    # can search article by title
    search_fields = ["title"]
    ordering = ["-datePublish"]
    class Media:
        js = (
            '/static/kindeditor-4.1.11-en/kindeditor-all-min.js',
            '/static/kindeditor-4.1.11-en/lang/zh_CN.js',
            '/static/kindeditor-4.1.11-en/config.js',
        )


class CArticle(models.Model):
    title = models.CharField(max_length=50, verbose_name='title')
    description = models.TextField(verbose_name='description', null=True)
    content = models.TextField(verbose_name='content')
    clickCnt = models.IntegerField(verbose_name='click Count', default=0)
    praiseCnt = models.IntegerField(verbose_name='praise Count', default=0)
    commentCnt = models.IntegerField(verbose_name='comment Count', default=0)
    datePublish = models.DateTimeField(verbose_name='date Publish', auto_now_add=True)
    # an article with higher priority will be shown on topper posion in article list
    # if priority is 0, will be shown in time order
    priority = models.IntegerField(verbose_name='priority', default=0)
    user = models.ForeignKey(CAuthor, verbose_name='Author')
    topCategoryId = models.ForeignKey(CTopCategory, verbose_name='top category', null=True, blank=True)
    subCategoryId = models.ForeignKey(CCategory, verbose_name='sub category', null=True, blank=True)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = verbose_name
        ordering = ['-datePublish']

    def __str__(self):
        return self.title
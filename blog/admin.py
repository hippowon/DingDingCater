# -*- coding: utf-8 -*-

from django.contrib import admin
import blog.models

admin.site.register(blog.models.CAuthor)
admin.site.register(blog.models.CTopCategory, blog.models.CTopCategoryManager)
admin.site.register(blog.models.CCategory, blog.models.CCategoryManager)
admin.site.register(blog.models.CArticle, blog.models.CArticleManager)







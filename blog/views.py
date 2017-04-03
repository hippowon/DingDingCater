# -*- coding: utf-8 -*-

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from DingDingCater import settings
from django.views.decorators.csrf import csrf_exempt
from blog import models
from blog.models import CCategory, CArticle
from django.core.paginator import EmptyPage, InvalidPage, PageNotAnInteger
from django.conf import settings
import os
import json
import datetime as dt
import time

@csrf_exempt
def page_index(request:HttpRequest):
    category_list = CCategory.objects.all()

    # get page number
    pageReq = int(request.GET.get('page', 1))
    if  pageReq == None:
        pageReq = 1

    # get page from list
    article_list = CArticle.objects.all()
    try:
        page_articles = models.getPageFromArticles(article_list, pageReq)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        page_articles = models.getPageFromArticles(article_list, 1)

    # get article recently published.
    article_list_recent = CArticle.objects.all().order_by("-datePublish")[:10]

    # get top click articles
    article_list_clickRank = CArticle.objects.all().order_by("-clickCnt")[:10]

    # get topest articles ( whose priority value is more than 100 )
    article_list_topest = CArticle.objects.all().filter(priority__gt=100).order_by("-priority")

    bShowGoToFirst, bShowGoToLast, firstPage, lastPage = getPaginatorInfo(pageReq, page_articles.paginator.num_pages)

    article_list_show = page_articles
    # create page number list for 'index.html' template。
    page_range = range(firstPage, lastPage + 1)

    bIsIndex = True
    return render(request, 'index.html', locals())

'''
 response for ajax request when user clicks praise button
'''
@csrf_exempt
def ajax_praiseCnt(request:HttpRequest):
    # update database
    articles = CArticle.objects.all().filter(id=request.POST["aid"])
    articles.update(praiseCnt=articles[0].praiseCnt+1)
    return HttpResponse(str(articles[0].praiseCnt))

'''
 calculate page number of the left most and right most, by pageReq and page_total.
 at the same time show 15 pages at most.
'''

def getPaginatorInfo(pageReq,page_total):
    bShowGoToLast = False
    bShowGoToFirst = False

    if page_total - pageReq < 7:
        bShowGoToLast = False
    else:
        bShowGoToLast = True

    if pageReq - 1 <= 7:
        bShowGoToFirst = False
    else:
        bShowGoToFirst = True

    firstPage = pageReq - 7
    if firstPage < 1:
        firstPage = 1
        bShowGoToFirst = False

    lastPage = firstPage + 15

    if lastPage >= page_total:
        lastPage = page_total
        firstPage = lastPage - 15
        if firstPage < 1:
            firstPage = 1
            bShowGoToFirst = False
        bShowGoToLast = False
    return  bShowGoToFirst,bShowGoToLast,firstPage,lastPage

# get category id and page number from "GET" request, return corresponding article list
# tcid: Top Category id
# scid: Sub Category id
def page_category(request:HttpRequest):
    tcidReq = request.GET.get('tcid', None)
    scidReq = request.GET.get('scid', None)

    bIsTopCategory = False

    article_list_recent = CArticle.objects.all().order_by("-datePublish")[:10]

    article_list_clickRank = CArticle.objects.all().order_by("-clickCnt")[:10]

    pageReq = int(request.GET.get('page', None))
    start = (pageReq - 1) * settings.ARTICLES_PERPAGE
    end = start + settings.ARTICLES_PERPAGE

    bIsIndex = False

    if tcidReq is not None and scidReq is not None: # sub category was clicked

        article_list = CArticle.objects.filter(topCategoryId=tcidReq).filter(subCategoryId=scidReq).order_by("-datePublish")

        try:
            page_articles = models.getPageFromArticles(article_list, pageReq)
        except (EmptyPage, InvalidPage, PageNotAnInteger):
            page_articles = models.getPageFromArticles(article_list, 1)

        try:
            article_list_show = CArticle.objects.filter(topCategoryId=tcidReq).filter(subCategoryId=scidReq).order_by("-datePublish")[start:end]
        except:
            article_list_show = CArticle.objects.filter(topCategoryId=tcidReq).filter(subCategoryId=scidReq).order_by("-datePublish")[0:settings.ARTICLES_PERPAGE]

        article_list_topest = CArticle.objects.filter(subCategoryId=scidReq).filter(priority__gt=0).order_by("-priority")

        bShowGoToFirst, bShowGoToLast, firstPage, lastPage = getPaginatorInfo(pageReq, page_articles.paginator.num_pages)
        page_range = range(firstPage, lastPage + 1)

        bIsTopCategory = False
        return render(request, 'index.html', locals())

    elif tcidReq is not None: # top category was clicked
        article_list = CArticle.objects.filter(topCategoryId=tcidReq).order_by("-datePublish")

        try:
            page_articles = models.getPageFromArticles(article_list, pageReq)
        except (EmptyPage, InvalidPage, PageNotAnInteger):
            page_articles = models.getPageFromArticles(article_list, 1)

        try:
            article_list_show = CArticle.objects.filter(topCategoryId=tcidReq).order_by("-datePublish")[start:end]
        except:
            article_list_show = CArticle.objects.filter(topCategoryId=tcidReq).order_by("-datePublish")[0:settings.ARTICLES_PERPAGE]

        article_list_topest = CArticle.objects.filter(topCategoryId=tcidReq).filter(priority__gt=0).order_by("-priority")

        bIsTopCategory = True
        bShowGoToFirst, bShowGoToLast, firstPage, lastPage = getPaginatorInfo(pageReq, page_articles.paginator.num_pages)
        page_range = range(firstPage, lastPage + 1)

        return render(request, 'index.html', locals())

    elif scidReq is not None:

        pass

    return render(request, 'index.html', locals())

'''
    return article's content
'''
def page_article(request:HttpRequest):
    article_list_recent = CArticle.objects.all().order_by("-datePublish")[:10]
    article_list_clickRank = CArticle.objects.all().order_by("-clickCnt")[:10]

	if article_id is not None:
        try:
            article = CArticle.objects.get(id=article_id)
        except :
            return page_index(request)
    else:
        article = CArticle.objects.get(id=0)

    ArticleID_previous = -1
    ArticleID_next = -1

    try:
        article_previous = article.get_previous_by_datePublish()
        ArticleID_previous = article_previous.id
    except(CArticle.DoesNotExist):
        ArticleID_previous = -1

    try:
        article_next = article.get_next_by_datePublish()
        ArticleID_next = article_next.id
    except(CArticle.DoesNotExist):
        ArticleID_next = -1

    # update click count
    CArticle.objects.filter(id=article_id).update(clickCnt=article.clickCnt + 1)
    return render(request, 'article.html', locals())


'''
        When clicking "upload" in KindEditor's uploading picture dialog,this function
    will be called.
        In this function, we can get pic's name and path. We should read pic data ,
    save it under a local static directory,and return pic's path to KindEditor。
        KindEditor will use this path(url) to request the pic and show in it's editor frame at once。

    KindEditor need JSON data as following format ：
    {"error": 1, "message": "error string "}
    {"error": 0, "url": "pic's path"}
'''
@csrf_exempt
def upload_image(request:HttpRequest, dirNameUnderUpload):
    if request.method == 'POST':
        result = {"error": 1, "message": "Error when upload pic"}
        img_upload = request.FILES.get("imgFile", None)
        if img_upload:
            # get suffix of pic file
            imgSuffix = img_upload.name.split(".")[-1]
            fileName_noSuffix = img_upload.name.split(".")[0]

            # create directory, one dir for one month
            today = dt.datetime.today()
            path_thisMonth = dirNameUnderUpload + '/%d/%d/' % (today.year, today.month)
            if not os.path.exists(settings.MEDIA_ROOT + path_thisMonth):
                os.makedirs(settings.MEDIA_ROOT + path_thisMonth)

            dirPath = os.path.join(settings.MEDIA_ROOT, path_thisMonth)

            if not os.path.exists(dirPath):
                os.makedirs(dirPath)

            # file format: add date after file name, for example, filename_20170201.jpg
            file_name = fileName_noSuffix + '_' + time.strftime('%Y%m%d', time.localtime(time.time())) + "." + imgSuffix

            # save pic
            open(os.path.join(dirPath, file_name), 'wb').write(img_upload.file.read())

            # assemble json data by json.dumps(), return to KindEditor
            # KindEditor will use this url to request the pic and show in it's editor frame。
            result = {"error": 0, "url": settings.MEDIA_URL + path_thisMonth + file_name}

        return HttpResponse(json.dumps(result), content_type="application/json")

# coding=utf-8
from django.shortcuts import render
from django.http import HttpResponse, QueryDict
from haystack.forms import SearchForm
import sys
from datetime import datetime
import time
from haystack.query import SQ, SearchQuerySet, EmptySearchQuerySet
from .models import SubjectTheme, Subject, View, FileBaseInfo, FileExtendInfo, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext
from django.shortcuts import render_to_response
import re
from collections import defaultdict
from django.http import HttpResponseRedirect

reload(sys)
sys.setdefaultencoding('utf-8')

from haystack.forms import SearchForm

def full_result_object(request):
	obj = FileBaseInfo.objects.all()
	tiaoshu = len(obj)
	#print tiaoshu
	return render_to_response('himalaya/full_result_object.html', {'obj': obj, 'tiaoshu': tiaoshu},
	                          context_instance=RequestContext(request))


def check_tree(itemid,id,ziduan,sets):
	field = Category.objects.filter(pid=id)
	for item in field:
		value = FileExtendInfo.objects.filter(fieldId=str(itemid),filedValue=str(item.id))
		id_set = set()
		for i in value:
			id_set.add(i.fileId)
		if(value.count()!=0):
			if sets:
				global tongji_dict
				if len(id_set.intersection(sets))!=0:
					tongji_dict[(item.attrName,ziduan)] = len(id_set.intersection(sets))
			else:
				global tongji_dict
				if len(id_set)!=0:
					tongji_dict[(item.attrName,ziduan)] = len(id_set)
		check_tree(itemid,item.id,ziduan,sets)


# 全库文献里的知识视图
def statisticInfo(request):
    """
    １　ｑ＝ｇｏ不做全文过滤,检索标识
    ２　时间特殊处理
    ３　其他字段统一检索
    ４　使用　request.GET　注意预先检查该键是否存在，以及键对应的值是否为空（空值，不参与检索）
    :param request:
    :return:
    """
    query = request.GET['q']
    if(query!=''):
        posts = SearchQuerySet().filter(content=query)
    else:
        posts = SearchQuerySet().all()
    for key in ['title', 'keywords', 'creator', 'language','fileFormat','spatial','discipline','fileType']:
        if request.GET.has_key(key) and request.GET[key]!=u'':
            posts = posts.filter_and(**{key: request.GET[key]})
    if request.GET.__contains__('inp_start_date'):
        start_date = request.GET['inp_start_date']
        if start_date:
            try:
                strcreatedate = ''
                if (int(start_date) >= 10000):
                    strcreatedate = str(start_date)[0:4]
                elif (len(str(start_date)) == 1):
                    if (int(start_date) == 0):
                        strcreatedate = '0001'
                    else:
                        strcreatedate = '000' + str(start_date)
                elif (len(str(start_date)) == 2):
                    strcreatedate = '00' + str(start_date)
                elif (len(str(start_date)) == 3):
                    strcreatedate = '0' + str(start_date)
                else:
                    strcreatedate = str(start_date)
                aa = (str(strcreatedate) + '/01/01').split('/')
                s_t = datetime.strptime(''.join(aa), "%Y%m%d").date()
                # print(s_t)
                posts = posts.filter_and(pubDate__gte=s_t)
            except ValueError:
                html = "<html><script>alert('请输入正确是年份 ！')</script></html>"
                return HttpResponse(html)
    if request.GET.__contains__('inp_end_date'):
        end_date = request.GET['inp_end_date']
        if end_date:
            strcreatedate = ''
            if (int(end_date) >= 10000):
                strcreatedate = str(end_date)[0:4]
            elif (len(str(end_date)) == 1):
                if (int(end_date) == 0):
                    strcreatedate = '0001'
                else:
                    strcreatedate = '000' + str(end_date)
            elif (len(str(end_date)) == 2):
                strcreatedate = '00' + str(end_date)
            elif (len(str(end_date)) == 3):
                strcreatedate = '0' + str(end_date)
            else:
                strcreatedate = str(end_date)
            aa = (str(strcreatedate) + '/01/01').split('/')
            e_t = datetime.strptime(''.join(aa), "%Y%m%d").date()
            posts = posts.filter_and(pubDate__lte=e_t)
    posts = posts.filter(check=True)
    posts = posts.order_by("-updateDate")
    sqs = posts.facet('fileFormat').facet('spatial').facet('discipline').facet('language').facet(
        'fileType').facet_counts()
    ret_num = posts.count()

    return render_to_response('himalaya/statisticInfo.html', {'posts': posts, 'num': ret_num, 'sqs': sqs, 'query': query},
                              context_instance=RequestContext(request))






# 专题检索
def subject_statisticInfo(request):
    """
    1. 前台返回扩展属性
    2. 前台默认提交当前专题
    3. 修复扩展字段组合查询ｂｕｇ
    :param request:
    :return:
    """
    query = request.GET['q']
    if (query != ''):
        posts = SearchQuerySet().filter(content=query)
    else:
        posts = SearchQuerySet().all()
    for key in ['title', 'keywords', 'creator', 'language', 'fileFormat', 'spatial', 'discipline', 'fileType']:
        if request.GET.has_key(key) and request.GET[key] != u'':
            posts = posts.filter_and(**{key: request.GET[key]})
    subject_name = request.GET['subjectName']
    posts_sub = Subject.objects.get(subjectName=subject_name)
    subject_id = posts_sub.id
    posts = posts.filter_and(subjecttype=subject_id)
    temp = SubjectTheme.objects.filter(subjectId=subject_id,fieldType='6')
    for extfeature in temp:
        if request.GET.has_key(str(extfeature.id)+'_ext'):
            posts = posts.filter_and(**{str(extfeature.id)+'_ext': request.GET[str(extfeature.id)+'_ext']})
    sqs = posts
    for extfeature in temp:
        if request.GET.has_key(str(extfeature.id)+'_ext'):
            cer = (request.GET[str(extfeature.id)+'_ext']).split('/', 1)
            path = str(int(cer[0]) + 1)+'/' + cer[1]
            print(path)
        else:
            path = '1'
        sqs = sqs.facet(str(extfeature.id) + '_ext', prefix=path, mincount=1)
    sqs = sqs.facet('fileFormat').facet('spatial').facet('discipline').facet('language').facet(
        'fileType').facet_counts()
    ret_num = posts.count()
    sub_theme = SubjectTheme.objects.filter(subjectId_id=subject_id).filter(fieldType=6).exclude(
		corrAttri='-1')
    return render(request, 'himalaya/subject_statisticInfo.html', {'posts': posts, 'query': query,
                                                            'num': ret_num, 'sqs': sqs,
                                                            'sub_theme': sub_theme})

#基础文献处理
def base_statisticInfo(request):
    base_type = u'基础文献'
    query = request.GET['q']
    if (query == ''):
        posts = SearchQuerySet().all()
    else:
        posts = SearchQuerySet().filter(content=query)
    for key in ['title', 'keywords', 'creator', 'language', 'fileFormat', 'spatial', 'discipline', 'fileType']:
        if request.GET.has_key(key) and request.GET[key] != u'':
            posts = posts.filter(**{key: request.GET[key]})
    posts = posts.filter_and(check=1).filter(subjecttype='-1')
    if request.GET.__contains__('inp_start_date'):
        start_date = request.GET['inp_start_date']
        if start_date:
            strcreatedate = ''
            if (int(start_date) >= 10000):
                strcreatedate = str(start_date)[0:4]
            elif (len(str(start_date)) == 1):
                if (int(start_date) == 0):
                    strcreatedate = '0001'
                else:
                    strcreatedate = '000' + str(start_date)
            elif (len(str(start_date)) == 2):
                strcreatedate = '00' + str(start_date)
            elif (len(str(start_date)) == 3):
                strcreatedate = '0' + str(start_date)
            else:
                strcreatedate = str(start_date)
            aa = (str(strcreatedate) + '/01/01').split('/')
            s_t = datetime.strptime(''.join(aa), "%Y%m%d").date()
            posts = posts.filter_and(pubDate__gte=s_t)

    if request.GET.__contains__('inp_end_date'):
        end_date = request.GET['inp_end_date']
        if end_date:
            strcreatedate = ''
            if (int(end_date) >= 10000):
                strcreatedate = str(end_date)[0:4]
            elif (len(str(end_date)) == 1):
                if (int(end_date) == 0):
                    strcreatedate = '0001'
                else:
                    strcreatedate = '000' + str(end_date)
            elif (len(str(end_date)) == 2):
                strcreatedate = '00' + str(end_date)
            elif (len(str(end_date)) == 3):
                strcreatedate = '0' + str(end_date)
            else:
                strcreatedate = str(end_date)
            aa = (str(strcreatedate) + '/01/01').split('/')
            e_t = datetime.strptime(''.join(aa), "%Y%m%d").date()
            posts = posts.filter_and(pubDate__lte=e_t)
    posts = posts.order_by("-updateDate")
    sqs = posts.facet('fileFormat').facet('spatial').facet('discipline').facet('language').facet(
        'fileType').facet_counts()
    ret_num = posts.count()
    # 得到面搜索结果
    # print query
    return render(request, 'himalaya/base_statisticInfo.html', {'posts': posts, 'num': ret_num,
                                                             'sqs': sqs, 'query': query,
                                                             'base_type': base_type})
# coding=utf-8
import copy
import json
from collections import defaultdict
from datetime import datetime
from urllib2 import *

import haystack.inputs
import simplejson
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from haystack.query import SearchQuerySet

from .models import SubjectTheme, Subject, View, FileBaseInfo, FileExtendInfo, Category

reload(sys)
sys.setdefaultencoding('utf-8')


# from sklearn.cluster import KMeans
# import spacy
# from gensim import corpora, models
# import  jieba
# Create your views here.
# 全文的高级检索
def advanced_search(request):
    """
    １　时间特殊处理
    ２　其他字段依次检索
    :param request:
    :return:
    """
    posts = SearchQuerySet().models(FileBaseInfo).all()
    # print(SearchQuerySet)
    # 分页效率用 zsy 添加
    page_num = request.GET.get('page')
    if page_num < 1:
        page_num = 1
    else:
        page_num = int(page_num)
    # 分页效率用 zsy 添加
    start_date = request.GET['inp_start_date']  #
    end_date = request.GET['inp_end_date']

    # s_t = datetime.strptime(start_date, '%Y-%m-%d')
    # posts = posts.filter_and(pubDate__gte=s_t)
    # posts = posts.filter_and(fileType__iexact=request.GET['fileType'])
    # #print(request.GET)
    # print 'list.....', request.GET.lists()
    for e in request.GET.lists():
        # print e[0], e[1]
        if e[0] not in ['inp_start_date', 'inp_end_date', 'page'] and e[1] != [u'']:
            for value in e[1]:
                if value != '':
                    posts = posts.filter_and(**{e[0]: value})
                # print 'value####', value
    # for q_key, value in request.GET.items():
    # 	#print 'q_key, value',q_key,value
    # 	# 是这里的问题 zsy加了‘page’
    # 	if q_key not in ['inp_start_date', 'inp_end_date', 'page'] and value:
    # 		posts = posts.filter_and(**{q_key: value})


    if request.GET['inp_start_date']:
        # if len(str(start_date))<4:
        strcreatedate = ''
        # #print 'startlen',len(str(start_date))
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
        # start_date = str(start_date) + '/01/01'
        aa = (str(strcreatedate) + '/01/01').split('/')
        s_t = datetime.strptime(''.join(aa), "%Y%m%d").date()
        # s_t = datetime.strptime(start_date, '%Y-%m-%d')
        # print(s_t)
        posts = posts.filter_and(pubDate__gte=s_t)

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
        # start_date = str(start_date) + '/01/01'
        aa = (str(strcreatedate) + '/01/01').split('/')
        e_t = datetime.strptime(''.join(aa), "%Y%m%d").date()
        # end_date = (str(end_date) + '/01/01')
        # e_t = datetime.strptime(end_date, '%Y/%m/%d')
        # print(e_t)
        posts = posts.filter_and(pubDate__lte=e_t)
    # print(posts)
    posts = posts.filter(check=True)
    posts = posts.order_by("score")
    # print 'post.cout', posts.count()
    sqs = posts.facet('fileFormat').facet('spatial').facet('discipline').facet('language').facet(
        'fileType').facet_counts()
    # #print posts.all().count()
    ret_num = posts.all().count()
    ret_base_type = []
    key_w = []

    for e in posts[(page_num - 1) * 5:page_num * 5]:
        # print e.keywords
        if e.keywrods:
            key_w.append(e.keywords.replace("；", ";").split(";"))
        else:
            key_w.append(e.keywords)
        # key_w.append(re.split(r'[;,\s]\s*', e.keywords))
        # #print re.split(r'[;,\s]\s*', e.keywords)
        # key_w.append(keyword)
        # print e.subjecttype
        if int(e.subjecttype) == -1:
            ret_base_type.append(u'基础文献')
        # print 'subtype==-1'
        else:
            sub_name = Subject.objects.get(id=int(e.subjecttype)).subjectName
            ret_base_type.append(sub_name)
        # print 'sub_name', sub_name

    posts = zip(posts[(page_num - 1) * 5:page_num * 5], ret_base_type, key_w)
    # zsy 分页效率改动添加
    for x in range(0, ret_num):
        if x not in range((page_num - 1) * 5, page_num * 5):
            posts.insert(x, x)
        else:
            continue
        # print '11111111111113456745', posts
        # zsy 分页效率添加
    query = ''
    ##############zsy 筛选条件
    c = request.GET.lists()
    choiceitems=[]
    for i in c:
        if (i[0] == 'fileFormat' or i[0] == 'spatial' or i[0] == 'discipline' or i[0] == 'pubDate'):
           choiceitems.append(i)
        if(i[0] == 'language' or i[0] == 'fileType'):
            if i[1][0]!=u'':
                choiceitems.append(i)
    print 'choiceitems',choiceitems
    ##############zsy 筛选条件
    return render(request, 'himalaya/show_1.html', {'posts': posts, 'query': query, 'num': ret_num, 'sqs': sqs,'choiceitems':choiceitems})


def check_tree(itemid, id, ziduan, sets):
    field = Category.objects.filter(pid=id)
    for item in field:
        value = FileExtendInfo.objects.filter(fieldId=str(itemid), filedValue=str(item.id))
        id_set = set()
        for i in value:
            id_set.add(i.fileId)
        if (value.count() != 0):
            if sets:
                global tongji_dict
                if len(id_set.intersection(sets)) != 0:
                    tongji_dict[(item.attrName, ziduan)] = len(id_set.intersection(sets))
            else:
                global tongji_dict
                if len(id_set) != 0:
                    tongji_dict[(item.attrName, ziduan)] = len(id_set)
        check_tree(itemid, item.id, ziduan, sets)


# 专题检索
def search_subject(request):
    """
    1. 前台返回扩展属性
    2. 前台默认提交当前专题
    3. 修复扩展字段组合查询ｂｕｇ
    :param request:
    :return:
    """
    # 修改一 zsy添加筛选标记 start
    choiceitems = []  # 存放树里要查找的项,eg.[[英语,language],[汉语，language]]
    typeitems = []
    check_repeat = 0
    ordertest = 1
    earlysubjectitems = []
    subjectitems =[]
    if request.GET.has_key('addtypes'):
        # page值
        if request.GET.has_key('page'):
            page_num = int(request.GET['page'])
        else:
            page_num = 1
        # 标记内容的类型
        types = request.GET['addtypes']
        typeitems.append(types)

        print  'types', types
        # 标记内容
        a = request.GET['addmark']
        typeitems.append(a)
        print 'addmark', a
        # 前面筛选过的树
        xx = request.session.get('earlychoiceitems')
        for i in xx:
            choiceitems.append(i)
            if i[1] == a:
                check_repeat = 1

        if check_repeat == 0:
            choiceitems.append(typeitems)

        query = request.session.get('qq')
        order = request.session.get('earlyorder')
        subject_name = request.session.get('subjectname')
        queryb = request.session.get('queryb')
        earlysubjectitems = request.session.get('earlysubjectitems')

        # print '进入点树过滤分支', types

        # 修改一 zsy添加筛选标记 end
        # 修改二 zsy chenged in 1-16 start (1)在删去一项树的过滤搜索 (2)点击不同排序方式时（3） 没点树-》点翻页 (4)没点树-》刚进或高级查询 start
    else:
        if request.GET.has_key('deletemark'):
            if request.GET.has_key('page'):
                page_num = int(request.GET['page'])
            else:
                page_num = 1
            choiceitems = request.session.get('earlychoiceitems')
            earlysubjectitems = request.session.get('earlysubjectitems')
            query = request.session.get('qq')
            order = request.session.get('earlyorder')
            queryb = request.session.get('queryb')
            subject_name = request.session.get('subjectname')
            deletemark = request.GET['deletemark']
            i = 0
            for item in choiceitems:
                print 'zzzzzzz', item[1]
                if item[1] == deletemark:
                    choiceitems.pop(i)
                    print 'item[0]', item[0]
                    print 'item', item
                    if item[0] == u'no':
                        j = 0
                        print 'earlysubjectitems', earlysubjectitems
                        for v in earlysubjectitems:
                            print 'deletetest', item[1], v[2].split('/', -1)[1]
                            if item[1] == v[2].split('/', -1)[1]:
                                earlysubjectitems.pop(j)
                            j += 1
                i += 1


            print '进入delete分支', deletemark,earlysubjectitems
        # 2.22添加用于rank排序 start 111111111111111111111111 zsy
        elif request.GET.has_key('rank'):
            if request.GET.has_key('page'):
                page_num = int(request.GET['page'])
            else:
                page_num = 1
            choiceitems = request.session.get('earlychoiceitems')
            query = request.session.get('qq')
            queryb = request.session.get('queryb')
            subject_name = request.session.get('subjectname')
            earlysubjectitems = request.session.get('earlysubjectitems')
            order = str(request.GET['rank'])
            print '进入rank分支', order
        # 2.22添加用于rank排序 end
        else:
            # 没点树-》点翻页
            if request.GET.has_key('page'):
                page_num = int(request.GET['page'])
                choiceitems = request.session.get('earlychoiceitems')
                earlysubjectitems = request.session.get('earlysubjectitems')
                order = request.session.get('earlyorder')
                query = request.session.get('qq')
                queryb = request.session.get('queryb')
                subject_name = request.session.get('subjectname')
                print 'querbbbb', queryb
                print '进入没点树 点翻页分支', page_num
            # 第一次进入时或高级查询
            else:

                print '进入初始分支'
                order = 'score'
                page_num = 1
                query = request.GET['q']

                queryb = request.GET.lists()
                request.session['queryb'] = request.GET.lists()

                if request.GET['subjectName']:
                    subject_name = request.GET['subjectName']
                else:
                    subject_name = request.session.get('subjectname')
                # print 'qqqqqqzzzzz', query
    # 修改二  zsy chenged in 1-16 end

    if (query != ''):
        posts = SearchQuerySet().filter(content=query)
    else:
        posts = SearchQuerySet().all()

    # 修改四 zsy 此处if else 设置高级搜索不受树过滤session约束 start
    if queryb:
        for key in queryb:
            if key[0] in ['title', 'keywords', 'creator', 'language', 'fileFormat', 'spatial', 'discipline',
                          'fileType']:
                for item in key[1]:
                    if item != u'':
                        posts = posts.filter_and(**{key[0]: haystack.inputs.Exact(item)})
    else:
        for key in request.GET.lists():
            if key[0] in ['title', 'keywords', 'creator', 'language', 'fileFormat', 'spatial', 'discipline',
                          'fileType']:
                for item in key[1]:
                    if item != u'':
                        posts = posts.filter_and(**{key[0]: haystack.inputs.Exact(item)})
    # 修改四 zsy 此处if else 设置高级搜索不受树过滤session约束 end

    # 修改三 zsy 在有树的搜索时 要额外进行对树的筛选 start   @@@@@@@@@bug: 先高级搜索在点树搜索数目无效
    for key_tree in choiceitems:
        if key_tree[0] in ['title', 'keywords', 'creator', 'language', 'fileFormat', 'spatial', 'discipline', 'fileType']:
            posts = posts.filter_and(**{key_tree[0]: haystack.inputs.Exact(key_tree[1])})
    # 修改三 zsy 在有树的搜索时 要额外进行对树的筛选 end

    # subject_name = request.GET['subjectName']
    posts_sub = Subject.objects.get(subjectName=subject_name)
    subject_id = posts_sub.id
    posts = posts.filter_and(subjecttype=subject_id)
    temp = SubjectTheme.objects.filter(subjectId=subject_id, fieldType='6')
    ext = []
    extn = {}
    #zsy添加
    repalace = []

    for extfeature in temp:
        extn[str(extfeature.id) + '_ext'] = extfeature.fieldName
        ext.append(str(extfeature.id) + '_ext')
        if request.GET.has_key(str(extfeature.id) + '_ext'):
            posts = posts.filter_and(**{str(extfeature.id) + '_ext': haystack.inputs.Exact(request.GET[str(extfeature.id) + '_ext'])})
            # zsy 添加 start
            c=request.GET[str(extfeature.id) + '_ext']
            repalace.append(c)
            # zsy 添加 end
    # zsy 添加 start
    for item in earlysubjectitems:
        print 'guo_0',item
        posts = posts.filter_and(**{item[1]: haystack.inputs.Exact(item[0])})
        # print 'zzzzzzzzzz', item
    # zsy 添加 end
    # zsy修改五 按不同方式（order）进行排序 start
    posts = posts.order_by(order)
    if order == '-updateDate':
        ordertest = 0
    # zsy修改五 按不同方式（order）进行排序 end

    sqs = posts
    
    testrepeat=1
    for extfeature in temp:
        if request.GET.has_key(str(extfeature.id) + '_ext'):
            cer = (request.GET[str(extfeature.id) + '_ext']).split('/', 1)
            path = str(int(cer[0]) + 1) + '/' + cer[1]
            # zsy 添加 start
            for test in earlysubjectitems:
                if path==test[2]:
                    testrepeat=0
            if testrepeat:
                pathtype = path
                subjecttype = str(extfeature.id) + '_ext'
                repalace.append(subjecttype)
                repalace.append(pathtype)
                earlysubjectitems.append(repalace)
                print 'earlysubjectitems',earlysubjectitems
            # zsy 添加 start
        else:
            path = '1'
        sqs = sqs.facet(str(extfeature.id) + '_ext', prefix=path, mincount=1)

    # zsy 添加 start
    for item in earlysubjectitems:
        sqs = sqs.facet(item[1], prefix=item[2], mincount=1)
        print 'zzzzzzzzrrrrrrrrzz', sqs.count()
    # zsy 添加 start

    sqs = sqs.facet('fileFormat').facet('spatial').facet('discipline').facet('language').facet(
        'fileType').facet('pubDate').facet_counts()
    ret_num = posts.count()
    print 'guo_2',sqs

    ###################################知识视图#######################################################

    request.session['subject_idd'] = subject_id
    if len(posts) != len(SearchQuerySet().filter_and(subjecttype=subject_id)):
        request.session['lists_keywords'] = [i[0] for i in posts.all().values_list('keywords') if
                                             i[0] != None and i[0] != u'None' and i[0] != u'']
        # print'lists_keywords', request.session['lists_keywords']
        if len(request.session['lists_keywords']) == 0 or len(request.session['lists_keywords']) < len(posts) / 3:
            request.session['lists_keywords'] = []
            request.session['lists_abstract'] = [i.object.description for i in posts if
                                                 i.object != None and i.object.description != None and i.object.description != u'']
            # print 'lists_abstract',request.session['lists_abstract']
        else:
            request.session['lists_abstract'] = []

    else:
        request.session['lists_keywords'] = [None]
        request.session['lists_abstract'] = [None]

    #########################################################################################
    request.session['sqs'] = sqs
    request.session['query'] = query
    request.session['ret_num'] = ret_num
    request.session['querys'] = request.GET.lists()
    request.session['ext'] = ext
    request.session['extn'] = extn

    # zsy修改六 start
    request.session['earlychoiceitems'] = choiceitems
    request.session['qq'] = query
    request.session['queryb'] = queryb
    request.session['page_num'] = page_num#不同方式排列用
    request.session['earlyorder'] = order #除了刚进、高级查询、点不同排序时都需要
    request.session['subjectname'] = subject_name #仅专题页面有

    request.session['earlysubjectitems'] = earlysubjectitems

    print 'querys',request.GET.lists()
    print 'choice',choiceitems
    print 'early',earlysubjectitems
    # zsy修改六  end

    ret_base_type = []
    key_w = []
    for e in posts[(page_num - 1) * 5:page_num * 5]:
        if e.keywords:
            keyword = e.keywords.replace("；", ";").split(";")
        else:
            keyword = e.keywords
        key_w.append(keyword)
        if int(e.subjecttype) == -1:
            ret_base_type.append(u'基础文献')
        else:
            sub_name = Subject.objects.get(id=int(e.subjecttype)).subjectName
            ret_base_type.append(sub_name)
    posts = zip(posts[(page_num - 1) * 5:page_num * 5], ret_base_type, key_w)
    for x in range(0, ret_num):
        if x not in range((page_num - 1) * 5, page_num * 5):
            posts.insert(x, x)
        else:
            continue
    sub_theme = SubjectTheme.objects.filter(subjectId_id=subject_id).filter(fieldType=6).exclude(
        corrAttri='-1')
    #print 'ppppp',posts

    return render(request, 'himalaya/subject_search.html', {'posts': posts, 'query': query,
                                                            'num': ret_num, 'sqs': sqs,
                                                            'sub_theme': sub_theme, 'choiceitems': choiceitems,
                                                            'ordertest':ordertest,'subject_name':subject_name})


# return redirect('search/advanced_search.html')
# 全文检索
def full_search(request):
    """
    １　ｑ＝ｇｏ不做全文过滤,检索标识
    ２　时间特殊处理
    ３　其他字段统一检索
    ４　使用　request.GET　注意预先检查该键是否存在，以及键对应的值是否为空（空值，不参与检索）
    :param request:
    :return:
    """
    # 修改一 zsy添加筛选标记 start
    choiceitems2 = []  # 存放树里要查找的项,eg.[[英语,language],[汉语，language]]
    typeitems = []
    check_repeat = 0
    ordertest = 1
    rangetime = '1900,2017'
    if request.GET.has_key('addtypes'):
        # page值
        if request.GET.has_key('page'):
            page_num = int(request.GET['page'])
        else:
            page_num = 1
        # 标记内容的类型
        types = request.GET['addtypes']
        typeitems.append(types)
        # print  'types', types
        # 标记内容
        a = request.GET['addmark']
        typeitems.append(a)
        # print 'addmark', a
        # 前面筛选过的树
        xx = request.session.get('earlychoiceitems2')
        for i in xx:
            choiceitems2.append(i)
            if i[1] == a:
                check_repeat = 1
        if check_repeat == 0:
            choiceitems2.append(typeitems)

        query = request.session.get('qq')
        order = request.session.get('earlyorder')
        queryb = request.session.get('queryb')

        # print '进入点树过滤分支', types

        # 修改一 zsy添加筛选标记 end

        # 修改二 zsy chenged in 1-16 start (1)在删去一项树的过滤搜索 (2)点击不同排序方式时（3） 没点树-》点翻页 (4)没点树-》刚进或高级查询 start
    else:
        if request.GET.has_key('deletemark'):
            if request.GET.has_key('page'):
                page_num = int(request.GET['page'])
            else:
                page_num = 1
            choiceitems2 = request.session.get('earlychoiceitems2')
            query = request.session.get('qq')
            order = request.session.get('earlyorder')
            queryb = request.session.get('queryb')
            deletemark = request.GET['deletemark']
            i = 0
            for item in choiceitems2:
                # print 'zzzzzzz', item[1]
                if item[1] == deletemark:
                    choiceitems2.pop(i)
                i += 1
            # print '进入delete分支', deletemark
        # 2.22添加用于rank排序 start 111111111111111111111111 zsy
        elif request.GET.has_key('rank'):
            if request.GET.has_key('page'):
                page_num = int(request.GET['page'])
            else:
                page_num = 1
            choiceitems2 = request.session.get('earlychoiceitems2')
            query = request.session.get('qq')
            queryb = request.session.get('queryb')
            order = str(request.GET['rank'])
            # print '进入rank分支', order
        # 2.22添加用于rank排序 end
        else:
            # 没点树-》点翻页
            if request.GET.has_key('page'):
                page_num = int(request.GET['page'])
                choiceitems2 = request.session.get('earlychoiceitems2')
                order = request.session.get('earlyorder')
                query = request.session.get('qq')
                queryb = request.session.get('queryb')
                # print 'querbbbb',queryb
                # print '进入没点树 点翻页分支', page_num
            # 第一次进入时或高级查询
            else:

                # print '进入初始分支'
                order = 'score'
                page_num = 1
                query = request.GET['q']

                queryb = request.GET.lists()
                request.session['queryb'] = request.GET.lists()

    # print 'qqqqqqzzzzz', query
    # 修改二  zsy chenged in 1-16 end


#################2017-06-26
    if (query != ''):
        posts = SearchQuerySet().filter(content=query)
    else:
        p = Subject.objects.filter(subVisible=False)
        posts = SearchQuerySet().all()
        for i in p:
            posts = posts.exclude(subjecttype=i.id)

    # 修改四 zsy 此处if else 设置高级搜索不受树过滤session约束 start
    if queryb:
        for key in queryb:
            if key[0] in ['title', 'keywords', 'creator', 'language', 'fileFormat', 'spatial', 'discipline', 'fileType']:
                for item in key[1]:
                    if item != u'':
                        posts = posts.filter_and(**{key[0]: haystack.inputs.Exact(item)})
    else:
        for key in request.GET.lists():
                if key[0] in ['title', 'keywords', 'creator', 'language', 'fileFormat', 'spatial', 'discipline', 'fileType']:
                    for item in key[1]:
                        if item != u'':
                            posts = posts.filter_and(**{key[0]: haystack.inputs.Exact(item)})
    # 修改四 zsy 此处if else 设置高级搜索不受树过滤session约束 end

    #修改三 zsy 在有树的搜索时 要额外进行对树的筛选 start   @@@@@@@@@bug: 先高级搜索在点树搜索数目无效
    for key_tree in choiceitems2:
        posts = posts.filter_and(**{key_tree[0]: haystack.inputs.Exact(key_tree[1])})
    #修改三 zsy 在有树的搜索时 要额外进行对树的筛选 end

    if request.GET.__contains__('inp_start_date'):
        start_date = request.GET['inp_start_date']
        if ',' in start_date:
            rangetime = start_date
            start_date = start_date.split(',')[0]
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
        if 'abc' in end_date:
            end_date=request.GET['inp_start_date'].split(',')[1]
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

    # zsy修改五 按不同方式（order）进行排序 start
    posts = posts.order_by(order)
    if order == '-updateDate':
        ordertest = 0
    # zsy修改五 按不同方式（order）进行排序 end


    sqs = posts.facet('fileFormat').facet('spatial').facet('discipline').facet('language').facet(
        'fileType').facet('pubDate').facet_counts()
    ##########################知识视图###########################################################

    if len(posts) != len(SearchQuerySet().all()):
        request.session['listf_keywords'] = [i[0] for i in posts.all().values_list('keywords') if
                                             i[0] != None and i[0] != u'None' and i[0] != u'']
        if len(request.session['listf_keywords']) == 0 or len(request.session['listf_keywords']) < len(posts) / 3:
            request.session['listf_keywords'] = []
            request.session['listf_abstract'] = [i.object.description for i in posts if
                                                 i.object != None and i.object.description != None and i.object.description != u'']
            # print 'lists_abstract',request.session['lists_abstract']
        else:
            request.session['listf_abstract'] = []
    else:
        request.session['listf_keywords'] = [None]
        request.session['listf_abstract'] = [None]
        ######################################################################################3
    ret_num = posts.count()
    request.session['sqs'] = sqs
    request.session['query'] = query
    request.session['ret_num'] = ret_num
    request.session['queryf'] = request.GET.lists()#高级检索
    # print "queryf",request.GET.lists()
    # zsy修改六 start
    request.session['earlychoiceitems2'] = choiceitems2
    request.session['qq'] = query
    request.session['queryb'] = queryb
    request.session['page_num'] = page_num #不同方式排列用
    request.session['earlyorder'] = order #除了刚进、高级查询、点不同排序时都需要
    # zsy修改六  end
    # print 'choice',choiceitems
    # print'query',query
    ret_base_type = []
    key_w = []
    for e in posts[(page_num - 1) * 5:page_num * 5]:
        if e.keywords:
            keyword = e.keywords.replace("；", ";").split(";")
        else:
            keyword = e.keywords
        key_w.append(keyword)
        if int(e.subjecttype) == -1:
            ret_base_type.append(u'基础文献')
        else:
            sub_name = Subject.objects.get(id=int(e.subjecttype)).subjectName
            ret_base_type.append(sub_name)

    posts = zip(posts[(page_num - 1) * 5:page_num * 5], ret_base_type, key_w)
    for x in range(0, ret_num):
        if x not in range((page_num - 1) * 5, page_num * 5):
            posts.insert(x, x)
        else:
            continue
    #################################2017-06-26
    dict_sub = {}
    sub = Subject.objects.all()
    for i in sub:
        list_sub = []
        if i.subParent != None:
            list_sub.append(str(i.subParent))
            if sub.filter(id=i.subParent.id)[0].subParent != None:
                list_sub.append(str(sub.filter(id=i.subParent.id)[0].subParent))
        dict_sub[i.subjectName] = '/'.join(list_sub[::-1])

    return render_to_response('himalaya/show_1.html',
                              {'rangetime':rangetime,'posts': posts, 'num': ret_num, 'sqs': sqs, 'query': query, 'choiceitems': choiceitems2,
                               'ordertest':ordertest,'dict_sub':dict_sub},
                              context_instance=RequestContext(request))


# 首页界面
# 专题滚动展示　和　最新添加基础文献展示
def home(request):
    posts = Subject.objects.all()
    base_posts = FileBaseInfo.objects.filter(subjecttype=-1).order_by('-updateDate')[:3]  # 展示最新添加的３个文献
    panorama_list = View.objects.order_by('-createDate')[:3]
    return render(request, 'himalaya/home.html',
                  {'posts': posts, 'base_posts': base_posts, 'panorama_list': panorama_list})


def base_search(request):
    base_type = u'基础文献'

    # 修改一 zsy添加筛选标记 start
    choiceitems1 = []  # 存放树里要查找的项,eg.[[英语,language],[汉语，language]]
    typeitems = []
    check_repeat=0
    ordertest=1
    rangetime='1900,2017'
    if request.GET.has_key('addtypes'):
        # page值
        if request.GET.has_key('page'):
            page_num = int(request.GET['page'])
        else:
            page_num = 1
        # 标记内容的类型
        types = request.GET['addtypes']
        typeitems.append(types)
        print  'types', types
        # 标记内容
        a = request.GET['addmark']
        typeitems.append(a)
        print 'addmark', a
        # 前面筛选过的树
        xx = request.session.get('earlychoiceitems1')
        for i in xx:
            choiceitems1.append(i)
            if i[1]== a:
                check_repeat=1
        if check_repeat==0:
            choiceitems1.append(typeitems)

        query = request.session.get('qq')
        order = request.session.get('earlyorder')
        queryb = request.session.get('queryb')

        print '进入点树过滤分支', types

    #修改一 zsy添加筛选标记 end

    #修改二 zsy chenged in 1-16 start (1)在删去一项树的过滤搜索 (2)点击不同排序方式时（3） 没点树-》点翻页 (4)没点树-》刚进或高级查询 start
    else:
        if request.GET.has_key('deletemark'):
            if request.GET.has_key('page'):
                page_num = int(request.GET['page'])
            else:
                page_num = 1
            choiceitems1 = request.session.get('earlychoiceitems1')
            query = request.session.get('qq')
            order = request.session.get('earlyorder')
            queryb = request.session.get('queryb')
            deletemark = request.GET['deletemark']
            i=0
            for item in choiceitems1:
                print 'zzzzzzz',item[1]
                if  item[1] == deletemark:
                    choiceitems1.pop(i)
                i += 1
            print '进入delete分支', deletemark
        # 2.22添加用于rank排序 start 111111111111111111111111 zsy
        elif request.GET.has_key('rank'):
            if request.GET.has_key('page'):
                page_num = int(request.GET['page'])
            else:
                page_num = 1
            choiceitems1 = request.session.get('earlychoiceitems1')
            query = request.session.get('qq')
            queryb = request.session.get('queryb')
            order=str(request.GET['rank'])
            print '进入rank分支', order,queryb
        #2.22添加用于rank排序 end
        else:
            #没点树-》点翻页
            if request.GET.has_key('page'):
                page_num = int(request.GET['page'])
                choiceitems1 = request.session.get('earlychoiceitems1')
                order = request.session.get('earlyorder')
                query = request.session.get('qq')
                queryb = request.session.get('queryb')
                # print '进入没点树 点翻页分支',page_num
            #第一次进入时
            else:
                # print '进入初始分支'
                order = 'score'
                page_num = 1
                query = request.GET['q']

                queryb = request.GET.lists()
                request.session['queryb'] = request.GET.lists()


    # print 'qqqqqqzzzzz', query
    #修改二  zsy chenged in 1-16 end

    if (query == ''):
        posts = SearchQuerySet().all()
    else:
        posts = SearchQuerySet().filter(content=query)

    # 修改四 zsy 此处if else 设置高级搜索不受树过滤session约束 start
    print"806"
    if queryb:
        print"enter",queryb
        for key in queryb:
            if key[0] in ['title', 'keywords', 'creator', 'language', 'fileFormat', 'spatial', 'discipline', 'fileType']:
                for item in key[1]:
                    if item != u'':
                        print"812"
                        posts = posts.filter_and(**{key[0]: haystack.inputs.Exact(item)})
                        print"813"
    else:
        print"enter else"
        for key in request.GET.lists():
                if key[0] in ['title', 'keywords', 'creator', 'language', 'fileFormat', 'spatial', 'discipline', 'fileType']:
                    for item in key[1]:
                        if item != u'':
                            print"820"
                            posts = posts.filter_and(**{key[0]: haystack.inputs.Exact(item)})
                            print"822"
    # 修改四 zsy 此处if else 设置高级搜索不受树过滤session约束 end

    print"out of queryb"
    #修改三 zsy 在有树的搜索时 要额外进行对树的筛选 start   @@@@@@@@@bug: 先高级搜索在点树搜索数目无效
    for key_tree in choiceitems1:
        print"828"
        posts = posts.filter_and(**{key_tree[0]: haystack.inputs.Exact(key_tree[1])}) ## 尝试模糊其他匹配方式？
        print"830"
    #修改三 zsy 在有树的搜索时 要额外进行对树的筛选 end
    print"834"
    posts = posts.filter_and(check=1).filter(subjecttype='-1')
    if request.GET.__contains__('inp_start_date'):
        start_date = request.GET['inp_start_date']
        if ',' in start_date:
            rangetime = start_date
            start_date=start_date.split(',')[0]
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
        if 'abc' in end_date:
            end_date=request.GET['inp_start_date'].split(',')[1]
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

    #zsy修改五 按不同方式（order）进行排序 start
    posts = posts.order_by(order)
    if order=='-updateDate':
        ordertest=0
    #zsy修改五 按不同方式（order）进行排序 end



    sqs = posts.facet('fileFormat').facet('spatial').facet('discipline').facet('language').facet(
        'fileType').facet('pubDate').facet_counts()
    ret_num = posts.count()
    ####################################################知识图谱###############

    if len(posts) != len(SearchQuerySet().filter(subjecttype='-1')):
        request.session['listb_keywords']  = [i[0] for i in posts.all().values_list('keywords') if i[0] != None and i[0] != u'None' and i[0] != u'']
        request.session['listb_creator'] = [i[0] for i in posts.all().values_list('creator') if i[0] != None and i[0] != u'None' and i[0] != u'']
        if len(request.session['listb_keywords']) == 0 or len(request.session['listb_keywords']) < len(posts) / 3:
            request.session['listb_keywords'] = []
            request.session['listb_abstract'] = [i.object.description for i in posts if
                                                 i.object != None and i.object.description != None and i.object.description != u'']
            # print 'lists_abstract',request.session['lists_abstract']
        else:
            request.session['listb_abstract'] = []
    else:
        request.session['listb_keywords'] = [None]
        request.session['listb_abstract'] = [None]
        request.session['listb_creator'] = [None]
        # print 'bababababa',request.session['listb_creator']
   ###########################################################################

    request.session['sqs'] = sqs
    request.session['query'] = query
    request.session['ret_num'] = ret_num
    request.session['queryb'] = queryb

    # zsy修改六 start
    request.session['earlychoiceitems1'] = choiceitems1
    request.session['qq'] = query
    request.session['page_num'] = page_num #不同方式排列用
    request.session['earlyorder'] = order #除了刚进、高级查询、点不同排序时都需要
    # zsy修改六  end

    key_w = []
    ret_base_type = []
    for e in posts[(page_num - 1) * 5:page_num * 5]:
        if e.keywords:
            keyword = e.keywords.replace("；", ";").split(";")
        else:
            keyword = e.keywords
        key_w.append(keyword)
        if int(e.subjecttype) == -1:
            ret_base_type.append(u'基础文献')
        else:
            sub_name = Subject.objects.get(id=int(e.subjecttype)).subjectName
            ret_base_type.append(sub_name)
    posts = zip(posts[(page_num - 1) * 5:page_num * 5], ret_base_type, key_w)
    for x in range(0, ret_num):
        if x not in range((page_num - 1) * 5, page_num * 5):
            posts.insert(x, x)
        else:
            continue

    return render(request, 'himalaya/basefile_search.html', {'rangetime':rangetime,'posts': posts, 'num': ret_num,
                                                             'sqs': sqs, 'query': query,
                                                             'base_type': base_type, 'choiceitems': choiceitems1,
                                                             'ordertest':ordertest})


def show(request):
    return render(request, 'himalaya/show.html')


def panorama(request):
    panorama_list = View.objects.order_by('-createDate')
    return render(request, 'himalaya/panorama.html', {'panorama_list': panorama_list})


from django.shortcuts import get_object_or_404


def detail(request, pk_id):
    """
    １　基础属性统一展示
    ２　扩展属性根据基础文献是否匹配专题，如果是，那么根据专题ｉｄ匹配出扩展属性
    ３　专题属性表　和　扩展表　联合查询出　字段和值，作为后台输出。
    :param request:
    :param pk_id:
    :return:
    """
    post = get_object_or_404(FileBaseInfo, pk=pk_id)
    file_id = post.id
    # print 'file_id', file_id
    # #print extend_attr

    if post.attachment.url.split('.')[-1] == 'pdf':
        # print 'pdf'
        post_pdf = True
    else:
        post_pdf = False

    # print '#########', post.attachment.url.split('.')[-1]
    if post.attachment.url.split('.')[-1] in ['mp4', 'avi']:
        post_mp4 = True
    else:
        post_mp4 = False
    # print "subjecttype", post.subjecttype
    if post.subjecttype == -1:
        extend_attr = None
    else:
        # extend_attr = Subject.objects.get(pk=extend_attr)
        # extend_attr = SubjectTheme.objects.filter(subjecttype=extend_attr)
        # 扩展属性表中查询该文件id对应的扩展字段值
        # print extend_attr.count()
        ret = []
        # for value in extend_attr:
        # 	fieldName = SubjectTheme.objects.get(id=value.fieldId).fieldName
        # 	if value.filedValue.isdigit():
        # 		try:
        # 			value = Category.objects.get(id=value.filedValue).attrName
        # 		except:
        # 			print 'no value'
        # 	if str(value) == '-1':
        # 		continue
        # 	ret.append((fieldName, value))
        # extend_attr = ret
        extend_attr = SubjectTheme.objects.filter(subjectId=post.subjecttype)
        for value in extend_attr:
            result = FileExtendInfo.objects.filter(fieldId=value.id, fileId=post.id)
            if result:
                fieldName = value.fieldName
                values = ''
                if value.fieldType == '6' or value.fieldType == '5':
                    for i, item in enumerate(result):
                        field = Category.objects.get(id=int(item.filedValue)).attrName
                        if i == 0:
                            values = field
                        else:
                            values = values + ',' + field
                else:
                    for i, item in enumerate(result):
                        if i == 0:
                            value = item.filedValue
                        else:
                            values = values + ',' + item.filedValue
                ret.append((fieldName, values))
        extend_attr = ret
    # field_name = extend_attr[0].fieldId
    # field_value = extend_attr[0]
    # print ret
    # #print extend_attr[0].filedValue
    # field_id = extend_attr[0].fieldId
    # sub_theme_fieldName = SubjectTheme.objects.get(pk=field_id)
    # #print '专题负责人',sub_theme_fieldName
    # extend_attr = (sub_theme_fieldName, extend_attr[0].filedValue)
    # #print post.fileType

    # morelikethis
    print type(pk_id)
    entry = FileBaseInfo.objects.get(id=int(pk_id))
    print 'entry',entry
    mlt = SearchQuerySet().more_like_this(entry)
    mlt = mlt[:4]
    print 'mlt', mlt
    # morelikethis

    return render(request, 'himalaya/detail.html',
                  {'post': post, 'extend_attr': extend_attr, 'post_pdf': post_pdf, 'post_mp4': post_mp4,'mlt':mlt})


# 专题展示页
def specialist(request):
    """
    １　专题展示页，点击进入后，可以进行该专题下的检索
    2 subject中找到专题对应ｉｄ，　subjecttheme中通过专题ｉｄ找到专题负责人(问题：专题属性中有多个值，如何取得专题负责人一项)
    即使取到专题ｆｉｅｌｄＩｄ后，可以取匹配字段值，不同专题同样采取字段ｉｄ＝１，那么取到的值不一定是专题对应的负责人。
    ＝＝＝＝表结构，应该适当修改＝＝＝
    :param request:
    :return:
    """
    # subject_name = request.GET['subjectName']
    # posts_sub = Subject.objects.filter(subjectName=subject_name)
    # subject_id = posts_sub[0].id

    specialist_list = Subject.objects.all()
    # specialist_list = specialist_list.order_by('score')
    count_lst = []
    subP_list = []
    for e in specialist_list:
        # print 'e.id', e.id
        count = SearchQuerySet().models(FileBaseInfo).filter(subjecttype=e.id).count()
        # print 'counts', count
        count_lst.append(count)
        subP_list.append(e.subParent)

    specialist_list = zip(specialist_list, count_lst)

    sub_count = zip(subP_list, count_lst)
    result = defaultdict(list)
    for i, j in sub_count:
        result[i].append(j)
    result1 = dict(result)
    for i, j in result1.items():
        result1[i] = sum(j)
    # extend_attr = FileExtendInfo.objects.filter(fileId=file_id)
    # #print extend_attr.count()
    # ret = []
    # for value in extend_attr:
    # 	fieldName = SubjectTheme.objects.get(id=value.fieldId).fieldName
    # 	#print 'value', value, fieldName
    # 	ret.append((fieldName, value))
    # field_name = extend_attr[0].fieldId
    # field_value = extend_attr[0]
    # #print ret
    # extend_attr = ret
    return render(request, 'himalaya/specialist.html', {'specialist_list': specialist_list,'result1': result1})


def fenye(request):

    # print tiaoshu
    return render_to_response('himalaya/maptest.html',context_instance=RequestContext(request))




def termfreq(request):
    times = time.time()
    conn = urlopen(
        'http://localhost:8983/solr/collection1/terms?terms.fl=text&terms.limit=20&wt=json')
    rsp = simplejson.load(conn)
    # conn1 = urlopen(
    #     'http://localhost:8983/solr/collection1/tvrh?q=*&indent=on&tv=true&tv.tf_idf=true&tv.fl=text&wt=json&rows=700&omitHeader=true')
    # rsp1 = simplejson.load(conn1)
    # rsp1 = rsp1['termVectors']
    # rsp1 = rsp1[2:]
    # tf1 = dict()
    # print(time.time() - times)
    # for item in rsp1[1::2]:
    #     term = item[3]
    #     te = []
    #     for i,j in enumerate(term[::2]):
    #         key = j
    #         value = term[i*2+1]
    #         val = []
    #         if key in tf1.keys():
    #             val = tf1[key]
    #             val[0] = val[0] + 1
    #             val[1] = val[1] +value[1]
    #         else:
    #             val.append(1)
    #             val.append(value[1])
    #         tf1[key] = val
    # result = sorted(tf1.iteritems(), key=lambda t: t[1][1], reverse=True)
    # print(time.time() - times)
    rsp = rsp['terms']['text']
    tf = dict()
    for i,item in enumerate(rsp[::2]):
        tf[item] = rsp[i*2+1]
    return render_to_response('himalaya/termfreq.html',{'result':tf.items()})



# def termfreq(request):
#     conn = urlopen(
#         'http://localhost:8983/solr/collection1/tvrh?q=*&indent=on&tv=true&tv.tf_idf=true&tv.df=true&tv.tf=true&tv.fl=text&wt=json')
#     rsp = simplejson.load(conn)
#     rsp = rsp['termVectors'][2:]
#     tf = dict()
#     for item in rsp[1::2]:
#         item = item[3]
#         for i, term in enumerate(item[::2]):
#             x = []
#             temp = item[i * 2 + 1]
#             if term in tf.keys():
#                 x  = tf[term]
#                 x[0] = x[0] + temp[1]
#                 x[2] = x[2] + temp[5]
#             else:
#                 x.append(temp[1])
#                 x.append(temp[3])
#                 x.append(temp[5])
#             tf[term] = x
#     result = sorted(tf.iteritems(), key=lambda t: t[1][2], reverse=True)
#     return render_to_response('himalaya/termfreq.html',{'result':result[0:100]})





########2016.11.11 08:20修改

def full_statistic(request):

    sqs = request.session.get('sqs')
    query = request.session.get('qq')
    ret_num = request.session.get('ret_num')
    queryf = request.session.get('queryf')
    choiceitems2 = request.session.get('earlychoiceitems2')
    #print 'qqqqq',queryf
    advancef = []
    temp = []
    advancef.append(query)
    for q in queryf:
        if (q[0] == u'language' or q[0] == u'creator' or q[0] == u'fileType' or q[0] == u'inp_start_date' or q[0] == u'keywords' or q[0] == u'title' or q[0] == u'inp_end_date'
            or q[0] == u'fileFormat' or q[0] == u'spatial' or q[0] == u'discipline') and q[1] != [u'']:
            temp.append(q[1])

    for u in temp:
        for uu in u:
            advancef.append(uu)
    
    for m in choiceitems2:
        advancef.append(m[1])

    advancef = filter(lambda x: str(x) != '', advancef)
    list_field = []
    language = []
    discipline = []
    type = []
    format = []
    spa = []
    name = {}
    if sqs:
        for field in sqs:
            list_field.append(field)
        fields = sqs[list_field[0]]


        list_type = []
        if u'fileType' in fields:
            list_type = fields[u'fileType']
        list_type = filter(lambda x: x[1] != 0, list_type)
        countt = 0
        for lt in list_type:
            type.append(lt[0])
            countt += lt[1]
        piet = copy.deepcopy(list_type)
        for pt in piet:
            pt[1] = float(pt[1]) / countt

        list_lan = []
        if u'language' in fields:
            list_lan = fields[u'language']
        list_lan = filter(lambda x: x[1] != 0, list_lan)
        countl = 0
        for ll in list_lan:
            language.append(ll[0])
            countl += ll[1]
        piel = copy.deepcopy(list_lan)
        for pl in piel:
            pl[1] = float(pl[1])/countl


        list_spa = []
        if u'spatial' in fields:
            list_spa = fields[u'spatial']
        list_spa = filter(lambda x: x[1] != 0, list_spa)
        counts = 0
        for ls in list_spa:
            spa.append(ls[0])
            counts += ls[1]
        pies = copy.deepcopy(list_spa)
        for ps in pies:
            ps[1] = float(ps[1]) / counts


        list_discipline = []
        if u'discipline' in fields:
            list_discipline = fields[u'discipline']
        list_discipline = filter(lambda x: x[1] != 0, list_discipline)
        countd = 0
        for ld in list_discipline:
            discipline.append(ld[0])
            countd += ld[1]
        pied = copy.deepcopy(list_discipline)
        for pd in pied:
            pd[1] = float(pd[1]) / countd
        #print 'jjjj',discipline


        list_format = []
        if u'fileFormat' in fields:
            list_format = fields[u'fileFormat']
        list_format = filter(lambda x: x[1] != 0, list_format)
        countf = 0
        for lf in list_format:
            format.append(lf[0])
            countf += lf[1]
        pief = copy.deepcopy(list_format)
        for pf in pief:
            pf[1] = float(pf[1]) / countf

        list_pubDate = []
        pubDate = []
        if u'pubDate' in fields:
            list_pubDate = fields[u'pubDate']
        list_pubDate = filter(lambda x: x[1] != 0, list_pubDate)
        list_pubDate.sort()
        count = 0
        for l in list_pubDate:
            l = list(l)
            l[0] = int(l[0][0:4])
            pubDate.append(l)

        l1 = ['文件类型',json.dumps('文件类型'), json.dumps(type), json.dumps(list_type),json.dumps(piet)]
        l2 = ['语言类型',json.dumps('语言类型'), json.dumps(language), json.dumps(list_lan), json.dumps(piel)]
        l3 = ['文件学科', json.dumps('文件学科'),json.dumps(discipline), json.dumps(list_discipline), json.dumps(pied)]
        l4 = ['空间范围',json.dumps('空间范围'), json.dumps(spa), json.dumps(list_spa), json.dumps(pies)]
        l5 = ['文件格式', json.dumps('文件格式'),json.dumps(format), json.dumps(list_format), json.dumps(pief)]
        top = [l1, l2, l3, l4, l5]
    #print 'top',top
    else:
        top = []
        pubDate = []
        ret_num = 0
        name = []
    return render(request, 'himalaya/full_statistic.html',
                                                          {'pubDate': json.dumps(pubDate),'name':name, 'top':top,
                                                            'query': query, 'ret_num':ret_num,'advancef':advancef,
                                                           })



def base_statistic(request):
    sqs = request.session.get('sqs')
    query = request.session.get('qq')
    ret_num = request.session.get('ret_num')
    queryb = request.session.get('queryb')
    choiceitems1 = request.session.get('earlychoiceitems1')
   
    advanceb = []
    temp = []
    advanceb.append(query)
    for q in queryb:
        if (q[0] == u'language' or q[0] == u'creator' or q[0] == u'fileType' or q[0] == u'inp_start_date' or q[0] == u'keywords' or q[0] == u'title' or q[0] == u'inp_end_date'
            or q[0] == u'fileFormat' or q[0] == u'spatial' or q[0] == u'discipline') and q[1] != [u'']:
            temp.append(q[1])
    for u in temp:
        for uu in u:
            advanceb.append(uu)
    for m in choiceitems1:
        advanceb.append(m[1])

    advanceb = filter(lambda x: str(x) != '',advanceb)


    list_field = []
    language = []
    discipline = []
    type = []
    format = []
    spa = []
    if sqs:
        for field in sqs:
            list_field.append(field)
        fields = sqs[list_field[0]]
        list_type = []
        if u'fileType' in fields:
            list_type = fields[u'fileType']

        list_type = filter(lambda x: x[1] != 0, list_type)
        countt = 0
        for lt in list_type:
            type.append(lt[0])
            countt += lt[1]
        piet = copy.deepcopy(list_type)
        for pt in piet:
            pt[1] = float(pt[1]) / countt

        list_lan = []
        if u'language' in fields:
            list_lan = fields[u'language']

        list_lan = filter(lambda x: x[1] != 0, list_lan)
        countl = 0
        for ll in list_lan:
            language.append(ll[0])
            countl += ll[1]
        piel = copy.deepcopy(list_lan)
        for pl in piel:
            pl[1] = float(pl[1]) / countl

        list_spa = []
        if u'spatial' in fields:
            list_spa = fields[u'spatial']


        list_spa = filter(lambda x: x[1] != 0, list_spa)
        counts = 0
        for ls in list_spa:
            spa.append(ls[0])
            counts += ls[1]
        pies = copy.deepcopy(list_spa)
        for ps in pies:
            ps[1] = float(ps[1]) / counts

        list_discipline = []
        if u'discipline' in fields:
            list_discipline = fields[u'discipline']

        list_discipline = filter(lambda x: x[1] != 0, list_discipline)
        countd = 0
        for ld in list_discipline:
            discipline.append(ld[0])
            countd += ld[1]
        pied = copy.deepcopy(list_discipline)
        for pd in pied:
            pd[1] = float(pd[1]) / countd

        list_format = []
        if u'fileFormat' in fields:
            list_format = fields[u'fileFormat']

        list_format = filter(lambda x: x[1] != 0, list_format)
        countf = 0
        for lf in list_format:
            format.append(lf[0])
            countf += lf[1]
        pief = copy.deepcopy(list_format)
        for pf in pief:
            pf[1] = float(pf[1]) / countf

        list_pubDate = []
        pubDate = []
        if u'pubDate' in fields:
            list_pubDate = fields[u'pubDate']

        list_pubDate = filter(lambda x: x[1] != 0, list_pubDate)
        list_pubDate.sort()
        count = 0
        for l in list_pubDate:
            l = list(l)
            l[0] = int(l[0][0:4])
            pubDate.append(l)


        l1 = ['文件类型', json.dumps('文件类型'), json.dumps(type), json.dumps(list_type), json.dumps(piet)]
        l2 = ['语言类型', json.dumps('语言类型'), json.dumps(language), json.dumps(list_lan), json.dumps(piel)]
        l3 = ['文件学科', json.dumps('文件学科'), json.dumps(discipline), json.dumps(list_discipline), json.dumps(pied)]
        l4 = ['空间范围', json.dumps('空间范围'), json.dumps(spa), json.dumps(list_spa), json.dumps(pies)]
        l5 = ['文件格式', json.dumps('文件格式'), json.dumps(format), json.dumps(list_format), json.dumps(pief)]
        top = [l1, l2, l3, l4, l5]

    else:
        pubDate = []
        top = []
        ret_num = 0


    return render(request, 'himalaya/base_statistic.html',
                  {'pubDate': json.dumps(pubDate),'top':top,
                   'query': query, 'ret_num': ret_num, 'advanceb':advanceb
                   })


def subject_statistic(request):

    sqs = request.session.get('sqs')
    query = request.session.get('qq')
    ret_num = request.session.get('ret_num')
    querys = request.session.get('querys')
    ext = request.session.get('ext')
    extn = request.session.get('extn')
    choiceitems = request.session.get('earlychoiceitems')
    subjectname = request.session.get('subjectname')

    advances = []
    advances.append(query)
    temp = []
    # print 'exexex',ext
    for q in querys:
        if 'ext' not in str(q[0]) and q[1] != [u''] and q[0] != u'subjectName' and q[0] != u'q'and q[0] != u'addmark' and q[0] != u'addtypes' and q[0] != u'page':
            advances.append(q[1][0])

    for m in choiceitems:
        advances.append(m[1])

    advances = filter(lambda x: str(x) != '',advances)
    #advances里面的检索条件没有去重复
    # print 'aaaaaaa',advances

    list_field = []
    language = []
    discipline = []
    type = []
    format = []
    spa = []
    if sqs:
        for field in sqs:
            list_field.append(field)
        fields = sqs[list_field[0]]

        #基础属性
        i = 0
        list_type = []
        if u'fileType' in fields:
            list_type = fields[u'fileType']


        list_type = filter(lambda x: x[1] != 0, list_type)
        countt = 0
        for lt in list_type:
            type.append(lt[0])
            countt += lt[1]
        piet = copy.deepcopy(list_type)
        for pt in piet:
            pt[1] = float(pt[1]) / countt

        list_lan = []
        if u'language' in fields:
            list_lan = fields[u'language']
        list_lan = filter(lambda x: x[1] != 0, list_lan)
        countl = 0
        for ll in list_lan:
            language.append(ll[0])
            countl += ll[1]
        piel = copy.deepcopy(list_lan)
        for pl in piel:
            pl[1] = float(pl[1]) / countl

        list_spa = []
        if u'spatial' in fields:
            list_spa = fields[u'spatial']
        list_spa = filter(lambda x: x[1] != 0, list_spa)
        counts = 0
        for ls in list_spa:
            spa.append(ls[0])
            counts += ls[1]
        pies = copy.deepcopy(list_spa)
        for ps in pies:
            ps[1] = float(ps[1]) / counts

        list_discipline = []
        if u'discipline' in fields:
            list_discipline = fields[u'discipline']
        list_discipline = filter(lambda x: x[1] != 0, list_discipline)
        countd = 0
        for ld in list_discipline:
            discipline.append(ld[0])
            countd += ld[1]
        pied = copy.deepcopy(list_discipline)
        for pd in pied:
            pd[1] = float(pd[1]) / countd

        list_format = []
        if u'fileFormat' in fields:
            list_format = fields[u'fileFormat']
        list_format = filter(lambda x: x[1] != 0, list_format)
        countf = 0
        for lf in list_format:
            format.append(lf[0])
            countf += lf[1]
        pief = copy.deepcopy(list_format)
        for pf in pief:
            pf[1] = float(pf[1]) / countf

        l1 = ['文件类型', json.dumps('文件类型'), json.dumps(type), json.dumps(list_type), json.dumps(piet)]
        l2 = ['语言类型', json.dumps('语言类型'), json.dumps(language), json.dumps(list_lan), json.dumps(piel)]
        l3 = ['文件学科', json.dumps('文件学科'), json.dumps(discipline), json.dumps(list_discipline), json.dumps(pied)]
        l4 = ['空间范围', json.dumps('空间范围'), json.dumps(spa), json.dumps(list_spa), json.dumps(pies)]
        l5 = ['文件格式', json.dumps('文件格式'), json.dumps(format), json.dumps(list_format), json.dumps(pief)]
        top = [l1, l2, l3, l4, l5]

        #扩展属性

        #收集时间
        list_194 = []
        name194 = []
        if u'194_ext' in fields:
            list_194 = fields[u'194_ext']
        list_194 = filter(lambda x: x[1] != 0, list_194)
        list_194.sort();
        count4 = 0
        for l4 in list_194:
            l4[0] = int(l4[0][2:6])
            name194.append(l4[0])
            count4 += l4[1]
        list194 = copy.deepcopy(list_194)
        for l4 in list194:
            l4[0] = str(l4[0])

        pie194 = copy.deepcopy(list_194)
        for p4 in pie194:
            p4[0] = str(p4[0])
            p4[1] = float(p4[1]) / count4


        list_pubDate = []
        pubDate = []
        if u'pubDate' in fields:
            list_pubDate = fields[u'pubDate']
        list_pubDate = filter(lambda x: x[1] != 0, list_pubDate)
        list_pubDate.sort()
        count = 0
        for l in list_pubDate:
            l = list(l)
            l[0] = int(l[0][0:4])
            pubDate.append(l)


        keeplist = []#全部的类型加数量
        list_id = []#对应keeplist中各类的属性id
        listname = []
        listnamej = []
        listcat = []
        for ex in fields:
            if '_ext' in str(ex) and '194_ext' not in str(ex):
                keeplist.append(fields[ex])
                listcat.append(fields[ex])
                list_id.append(ex)

        for le in keeplist:
            for lle in le:
                ss = lle[0]
                ss = ss.split('/',-1)
                ss = ss[-1]
                lle[0] = ss
        i = 0
        while i < len(keeplist):
            keeplist[i] = json.dumps(keeplist[i])
            i += 1

        for id in list_id:
            if id in extn:
                listname.append(extn[id])
                listnamej.append(json.dumps(extn[id]))

        for c in listcat:
            for cc in c:
                cc = cc.remove(cc[1])
        j = 0
        listcat2 = []
        for k in listcat:
            listcat1 = []
            for kk in k:
                listcat1.append(kk[0])

            listcat2.append(listcat1)

        listcat2 = map(json.dumps, listcat2)


        allex = zip(listname,listnamej, listcat2, keeplist)

    else:
        allex = zip()
        list_194 = []
        ret_num = 0
        pubDate = []
        name194 = []
        pie194 = []
        list194 = []
        top = []

    return render(request, 'himalaya/subject_statistic.html',
                  { 'list_194': json.dumps(list_194), 'name194': json.dumps(name194), 'pie194': json.dumps(pie194),'list194':json.dumps(list194),
                   'query': query,'ret_num':ret_num,'advances':advances,'top':top, 'allex':allex,'subjectname':subjectname,
                   'pubDate': json.dumps(pubDate), 


                   })

##################2017-06-26
# def sub_specialist(request):
#     if request.GET['id']:
#         sid = request.GET['id']
#
#     specialist_list = Subject.objects.filter(subParent=sid)
#     count_lst = []
#     for e in specialist_list:
#         count = SearchQuerySet().models(FileBaseInfo).filter(subjecttype=e.id).count()
#         count_lst.append(count)
#
#     specialist_list = zip(specialist_list, count_lst)
#
#     return render(request, 'himalaya/sub_specialist.html', {'specialist_list': specialist_list})
#
#
# ##############知识视图
# def sub_keywords(request):
#
#     query = request.session.get('qq')
#     ret_num = request.session.get('ret_num')
#     querys = request.session.get('querys')
#     choiceitems = request.session.get('earlychoiceitems')
#     subjectname = request.session.get('subjectname')
#
#     advances = []
#     advances.append(query)
#     temp = []
#     # print 'exexex',ext
#     for q in querys:
#         if 'ext' not in str(q[0]) and q[1] != [u''] and q[0] != u'subjectName' and q[0] != u'q' and q[
#             0] != u'addmark' and q[0] != u'addtypes' and q[0] != u'page' and q[0] != u'rank':
#             advances.append(q[1][0])
#
#     for m in choiceitems:
#         advances.append(m[1])
#     advances = filter(lambda x: str(x) != '', advances)
#     list_coN = range(1, 16)
#     list_num = range(10, 51)
#
#     return render(request, 'himalaya/sub_keywords.html', {'query': query, 'ret_num': ret_num, 'advances': advances,
#                                                           'subjectname': subjectname, 'list_coN': list_coN,
#                                                           'list_num': list_num})
#
#
# def keywords_s(request):
#     lists_abstract = request.session.get('lists_abstract')
#     lists_keywords = request.session.get('lists_keywords')
#     subject_idd = request.session.get('subject_idd')
#     val = 2
#     val1 = 30
#     if request.GET.has_key('co'):
#         if request.GET['co']:
#             val = request.GET['co']
#     if request.GET.has_key('nums'):
#         if request.GET['nums']:
#             val1 = request.GET['nums']
#
#     keyall = []
#     keylistAll = []
#     nodedic = {}
#     nodes = []
#     edges = []
#     maxnum = 0
#     maxco = 0
#     if lists_abstract == [None] and lists_keywords == [None]:
#         qk = FileBaseInfo.objects.filter(subjecttype=subject_idd).values_list('keywords')
#         qk = filter(lambda x: x[0] != None and x[0] != u'None' and x[0] != u'', qk)
#         lists_keywords = [i[0] for i in qk]
#         if lists_keywords == []:
#             qa = FileBaseInfo.objects.filter(subjecttype=subject_idd).values_list('description')
#             qa = filter(lambda x: x[0] != None and x[0] != u'None' and x[0] != u'', qa)
#             lists_abstract = [i[0] for i in qa]
#
#     if len(lists_keywords) != 0:
#         for keyword in lists_keywords:
#             keyword = keyword.replace('\xe2\x80\xa2', '\xc2\xb7')
#             keyword = re.sub(' +', '', keyword)
#             keyword = keyword.replace('；', ';')
#             keylist = keyword.split(';')
#
#             for v in range(len(keylist)):
#                 keylist[v] = keylist[v].strip()
#                 if keylist[v] != u'' and keylist[v] != '\n':
#                     keyall.append(keylist[v])
#
#             keylistAll.append(keylist)
#
#         counts = dict(Counter(keyall).most_common(int(val1)))
#         maxnum = Counter(keyall).most_common(int(val1))[0][1]
#         num = 0
#         for k, v in counts.items():
#             tdict = {}
#             tdict['name'] = k
#             tdict['value'] = v
#             nodes.append(tdict)
#             nodedic[k] = num
#             num += 1
#         # print nodedic
#         matx = zeros((len(nodedic), len(nodedic)))
#         # print keylistAll
#         for k, v in nodedic.items():
#             for m in keylistAll:
#                 for mi in range(len(m)):
#                     if m[mi] == k:
#                         m[mi] = v
#         kk = 0
#         for keyInx in keylistAll:
#             combine = itertools.combinations(keyInx, 2)
#             for j in combine:
#                 j = sorted(j)
#                 try:
#                     matx[j[0]][j[1]] += 1
#                 except:
#                     kk += 1
#         try:
#             maxco = amax(matx)
#         except:
#             maxco = 0
#
#         for i in range(len(nodedic)):
#             for j in range(len(nodedic)):
#                 edict = {}
#                 if matx[i][j] != 0 and matx[i][j] >= int(val):
#                     edict['source'] = i
#                     edict['target'] = j
#                     edict['value'] = matx[i][j]
#                     edges.append(edict)
#
#     elif len(lists_abstract) != 0:
#         list_cut = []
#         jieba.load_userdict("dict/userdict.txt")
#         for abstract in lists_abstract:
#             abstract = abstract.replace('\xe2\x80\xa2', '_')
#             abstract = abstract.replace('\xc2\xb7', '_')
#             abstract = abstract.replace('-', '_')
#             fenci = jieba.cut(abstract)
#             fenci = list(fenci)
#             fenci2 = [x for x in fenci if len(x) > 1]
#             fencis = ' '.join(fenci2)
#             fencis = re.sub("_", "\xc2\xb7".decode('utf-8'), fencis)
#             list_cut.append(fencis)
#
#         stoplist = []
#         with open('dict/ch_stopword.txt', 'r') as fr:
#             for line in fr:
#                 line = re.sub('\n', '', line)
#                 stoplist.append(line)
#             texts = [[word for word in document.split() if word not in stoplist]
#                      for document in list_cut]
#
#             # #去掉只出现一次的单词
#             frequency = defaultdict(int)
#             for text in texts:
#                 for token in text:
#                     frequency[token] += 1
#             texts = [[token for token in text if frequency[token] > 1]
#                      for text in texts]
#             dictionarygl = corpora.Dictionary(texts)
#             dictiongl = dictionarygl.token2id
#
#             corpus = [dictionarygl.doc2bow(text) for text in texts]
#
#             tfidf_model = models.TfidfModel(corpus)
#             tfidf = tfidf_model[corpus]
#             lista = []
#             listw = []
#             nodes = []
#             edges = []
#             nodedic = {}
#             for i in tfidf:
#                 temp = []
#                 i = sorted(i, key=lambda x: x[1], reverse=True)
#                 temp = i[0:6]
#
#                 for k, v in dictiongl.items():
#                     for j in range(len(temp)):
#                         temp[j] = list(temp[j])
#                         if temp[j][0] == v:
#                             temp[j][0] = k
#                 lista.append([x[0] for x in temp])
#                 listw.extend([x[0] for x in temp])
#
#             counts = dict(Counter(listw).most_common(int(val1)))
#             maxnum = Counter(listw).most_common(int(val1))[0][1]
#             num = 0
#             for k, v in counts.items():
#                 tdict = {}
#                 tdict['name'] = k
#                 tdict['value'] = v
#                 nodes.append(tdict)
#                 nodedic[k] = num
#                 num += 1
#
#             matx = zeros((len(nodedic), len(nodedic)))
#
#             for k, v in nodedic.items():
#                 for m in lista:
#                     for mi in range(len(m)):
#                         if m[mi] == k:
#                             m[mi] = v
#
#             kk = 0
#             for keyInx in lista:
#                 combine = itertools.combinations(keyInx, 2)
#                 for j in combine:
#                     j = sorted(j)
#                     try:
#                         matx[j[0]][j[1]] += 1
#                     except:
#                         kk += 1
#             try:
#                 maxco = amax(matx)
#             except:
#                 maxco = 0
#
#             for i in range(len(nodedic)):
#                 for j in range(len(nodedic)):
#                     edict = {}
#
#                     if matx[i][j] != 0 and matx[i][j] >= int(val):
#                         edict['source'] = i
#                         edict['target'] = j
#                         edict['value'] = matx[i][j]
#                         edges.append(edict)
#
#     return render_to_response('himalaya/keywords_s.html',{'nodes': json.dumps(nodes), 'edges': json.dumps(edges),'maxco':maxco,'maxnum':maxnum})
#
#
#
# def sub_cluster(request):
#     query = request.session.get('qq')
#     ret_num = request.session.get('ret_num')
#     querys = request.session.get('querys')
#     choiceitems = request.session.get('earlychoiceitems')
#     subjectname = request.session.get('subjectname')
#     subject_idd = request.session.get('subject_idd')
#
#     # print lists_keywords
#
#     advances = []
#     advances.append(query)
#     temp = []
#     # print 'exexex',ext
#     for q in querys:
#         if 'ext' not in str(q[0]) and q[1] != [u''] and q[0] != u'subjectName' and q[0] != u'q' and q[
#             0] != u'addmark' and q[0] != u'addtypes' and q[0] != u'page' and q[0] != u'rank':
#             advances.append(q[1][0])
#
#     for m in choiceitems:
#         advances.append(m[1])
#     advances = filter(lambda x: str(x) != '', advances)
#
#     list_class = range(1,11)
#     return render(request, 'himalaya/sub_cluster.html',{'query': query, 'ret_num': ret_num,
#                                                         'advances': advances, 'subjectname':subjectname,
#                                                         'list_class':list_class})
#
#
# def cluster_s(request):
#     lists_abstract = request.session.get('lists_abstract')
#     lists_keywords = request.session.get('lists_keywords')
#     subject_idd = request.session.get('subject_idd')
#     keyall = []
#     keylistAll = []
#     nodedic = {}
#     listr = []
#
#     val = 5
#     if request.GET.has_key('cs'):
#         if request.GET['cs']:
#             val = request.GET['cs']
#
#     if lists_abstract == [None] and lists_keywords == [None]:
#         qk = FileBaseInfo.objects.filter(subjecttype=subject_idd).values_list('keywords')
#         qk = filter(lambda x: x[0] != None and x[0] != u'None' and x[0] != u'', qk)
#         lists_keywords = [i[0] for i in qk]
#         if lists_keywords == []:
#             qa = FileBaseInfo.objects.filter(subjecttype=subject_idd).values_list('description')
#             qa = filter(lambda x: x[0] != None and x[0] != u'None' and x[0] != u'', qa)
#             lists_abstract = [i[0] for i in qa]
#     # print len(lists_keywords) != 0,lists_keywords
#     if len(lists_keywords) != 0:
#         new_model = gensim.models.KeyedVectors.load_word2vec_format('wiki.zh.text.vector.bin', binary=True)
#
#         for keyword in lists_keywords:
#             keyword = keyword.replace('\xe2\x80\xa2', '\xc2\xb7')
#             keyword = re.sub(' +', '', keyword)
#             keyword = keyword.replace('；', ';')
#             keylist = keyword.split(';')
#
#             for v in range(len(keylist)):
#                 keylist[v] = keylist[v].strip()
#                 keylist[v] = re.sub('[0,9]*:', '', keylist[v])
#                 if keylist[v] != u'':
#                     keyall.append(keylist[v])
#
#             keylistAll.append(keylist)
#         key = []
#         error = []
#         alist = []
#         # listr = []
#         token_num = len(Counter(keyall))
#         if token_num > 35:
#             topN = 35
#         else:
#             topN = token_num
#
#         counts = dict(Counter(keyall).most_common(topN))
#
#         for word, value in counts.items():
#             try:
#                 vector = new_model[word]
#                 key.append(word)
#                 alist.append(vector)
#             except:
#                 error.append(word)
#
#         num_clusters = int(val)
#         km_cluster = KMeans(n_clusters=num_clusters, max_iter=500, n_init=40, init='k-means++', n_jobs=1)
#         km_result = km_cluster.fit_predict(alist)
#         index = zip(km_result, key)
#         result = defaultdict(list)
#         for i, j in index:
#             result[i].append(j)
#         for k, v in result.items():
#             dictr = {}
#             dictr['name'] = 'class ' + str(k)
#             dictr['y'] = len(v)
#             dictr['Keywords'] = '; '.join(v)
#             listr.append(dictr)
#     elif len(lists_abstract) != 0:
#         new_model = gensim.models.KeyedVectors.load_word2vec_format('wiki.zh.text.vector.bin', binary=True)
#         list_cut = []
#         jieba.load_userdict("dict/userdict.txt")
#         for abstract in lists_abstract:
#             abstract = abstract.replace('\xe2\x80\xa2', '_')
#             abstract = abstract.replace('\xc2\xb7', '_')
#             abstract = abstract.replace('-', '_')
#             fenci = jieba.cut(abstract)
#             fenci = list(fenci)
#             fenci2 = [x for x in fenci if len(x) > 1]
#             fencis = ' '.join(fenci2)
#             fencis = re.sub("_", "\xc2\xb7".decode('utf-8'), fencis)
#             list_cut.append(fencis)
#
#         stoplist = []
#         with open('dict/ch_stopword.txt', 'r') as fr:
#             for line in fr:
#                 line = re.sub('\n', '', line)
#                 stoplist.append(line)
#             texts = [[word for word in document.split() if word not in stoplist]
#                      for document in list_cut]
#
#             # 去掉只出现一次的单词
#             frequency = defaultdict(int)
#             for text in texts:
#                 for token in text:
#                     frequency[token] += 1
#             texts = [[token for token in text if frequency[token] > 1]
#                      for text in texts]
#             dictionary = corpora.Dictionary(texts)
#             diction = dictionary.token2id
#             corpus = [dictionary.doc2bow(text) for text in texts]
#
#             tfidf_model = models.TfidfModel(corpus)
#             tfidf = tfidf_model[corpus]
#             listw = []
#             for i in tfidf:
#                 temp = []
#                 if len(i) != 0:
#                     i = sorted(i, key=lambda x: x[1], reverse=True)
#                     temp = i[0:6]
#                     for k, v in diction.items():
#                         for j in range(len(temp)):
#                             temp[j] = list(temp[j])
#                             if temp[j][0] == v:
#                                 temp[j][0] = k
#
#                 listw.extend([x[0] for x in temp])
#
#             token_num = len(Counter(listw))
#             if token_num > 35:
#                 topN = 35
#             else:
#                 topN = token_num
#             count = dict(Counter(listw).most_common(topN))
#             alist = []
#             wlist = []
#             error = []
#             for word in count:
#                 try:
#                     vector = new_model[word]
#                     wlist.append(word)
#                     alist.append(vector)
#                 except:
#                     error.append(word)
#
#         num_clusters = int(val)
#         km_cluster = KMeans(n_clusters=num_clusters, max_iter=800, n_init=40, init='k-means++', n_jobs=1)
#         km_result = km_cluster.fit_predict(alist)
#         index = zip(km_result, wlist)
#         result = defaultdict(list)
#         for i, j in index:
#             result[i].append(j)
#         # listr = []
#         for k, v in result.items():
#             dictr = {}
#             dictr['name'] = 'class ' + str(k)
#             dictr['y'] = len(v)
#             dictr['Keywords'] = '; '.join(v)
#             listr.append(dictr)
#     # print len(listr)
#     return render_to_response('himalaya/cluster_s.html',{'listr':json.dumps(listr),'listr2':listr})
#
#
#
#
# def base_keywords(request):
#     query = request.session.get('qq')
#     ret_num = request.session.get('ret_num')
#     queryb = request.session.get('queryb')
#     choiceitems1 = request.session.get('earlychoiceitems1')
#
#     advanceb = []
#     temp = []
#     advanceb.append(query)
#     for q in queryb:
#         if (q[0] == u'language' or q[0] == u'creator' or q[0] == u'fileType' or q[0] == u'inp_start_date' or q[
#             0] == u'keywords' or q[0] == u'title' or q[0] == u'inp_end_date'
#             or q[0] == u'fileFormat' or q[0] == u'spatial' or q[0] == u'discipline') and q[1] != [u'']:
#             temp.append(q[1])
#     for u in temp:
#         for uu in u:
#             advanceb.append(uu)
#     for m in choiceitems1:
#         advanceb.append(m[1])
#
#     advanceb = filter(lambda x: str(x) != '', advanceb)
#     list_coN = range(1, 21)
#     list_num = range(10, 51)
#     return render(request, 'himalaya/base_keywords.html', {'query': query, 'ret_num': ret_num, 'advanceb': advanceb,
#                                                            'list_coN': list_coN, 'list_num': list_num})
#
#
# def keywords_b(request):
#     listb_keywords = request.session.get('listb_keywords')
#     listb_abstract = request.session.get('listb_abstract')
#     val = 5
#     if request.GET.has_key('basek'):
#         if request.GET['basek']:
#             val = request.GET['basek']
#
#     val1 = 50
#     if request.GET.has_key('numb'):
#         if request.GET['numb']:
#             val1 = request.GET['numb']
#     maxnum = 0
#     maxco = 0
#     keyall = []
#     keylistAll = []
#     nodedic = {}
#     nodes = []
#     edges = []
#     if listb_keywords == [None] and listb_abstract == [None]:
#         qk = FileBaseInfo.objects.filter(subjecttype=-1).values_list('keywords')
#         qk = filter(lambda x: x[0] != None and x[0] != u'None' and x[0] != u'', qk)
#         listb_keywords = [i[0] for i in qk if i[0] != None]
#         if listb_keywords == []:
#             qa = FileBaseInfo.objects.all().values_list('description')
#             qa = filter(lambda x: x[0] != None and x[0] != u'None' and x[0] !=u'', qa)
#             listb_abstract = [i[0] for i in qa if i[0] != None]
#
#     if len(listb_keywords) != 0:
#         for keyword in listb_keywords:
#             keyword = keyword.replace('HimalayaMountain', 'Himalaya Mountain')
#             keyword = keyword.replace('\xe2\x80\xa2', '\xc2\xb7')
#             keyword = keyword.replace('&', ';')
#             keyword = keyword.replace('--', ';')
#             keyword = keyword.replace(',', ';')
#             keyword = keyword.replace('；', ';')
#             keylist = keyword.split(';')
#             for v in range(len(keylist)):
#                 keylist[v] = keylist[v].strip()
#                 keylist[v] = re.sub('[0,9]*:', '', keylist[v])
#                 if keylist[v] != u'':
#                     keyall.append(keylist[v])
#
#             keylistAll.append(keylist)
#         # print keyall
#
#         counts = dict(Counter(keyall).most_common(int(val1)))
#         maxnum = Counter(keyall).most_common(int(val1))[0][1]
#         # print 'ccc',counts
#         num = 0
#         for k, v in counts.items():
#             tdict = {}
#             tdict['name'] = k
#             tdict['value'] = v
#             nodes.append(tdict)
#             nodedic[k] = num
#             num += 1
#         # print nodedic
#         matx = zeros((len(nodedic), len(nodedic)))
#         # print keylistAll
#         for k, v in nodedic.items():
#             for m in keylistAll:
#                 for mi in range(len(m)):
#                     if m[mi] == k:
#                         m[mi] = v
#         kk = 0
#         for keyInx in keylistAll:
#             combine = itertools.combinations(keyInx, 2)
#             for j in combine:
#                 j = sorted(j)
#                 try:
#                     matx[j[0]][j[1]] += 1
#                 except:
#                     kk += 1
#         try:
#             maxco = amax(matx)
#         except:
#             maxco = 0
#
#         for i in range(len(nodedic)):
#             for j in range(len(nodedic)):
#                 edict = {}
#                 if matx[i][j] != 0 and matx[i][j] >= int(val):
#                     edict['source'] = i
#                     edict['target'] = j
#                     edict['value'] = matx[i][j]
#                     edges.append(edict)
#     elif len(listb_abstract) != 0:
#         list_cut = []
#         jieba.load_userdict("dict/userdict.txt")
#         for abstract in listb_abstract:
#             abstract = abstract.replace('\xe2\x80\xa2', '_')
#             abstract = abstract.replace('\xc2\xb7', '_')
#             abstract = abstract.replace('-', '_')
#             fenci = jieba.cut(abstract)
#             fenci = list(fenci)
#             fenci2 = [x for x in fenci if len(x) > 1]
#             fencis = ' '.join(fenci2)
#             fencis = re.sub("_", "\xc2\xb7".decode('utf-8'), fencis)
#             list_cut.append(fencis)
#
#         stoplist = []
#         with open('dict/ch_stopword.txt', 'r') as fr:
#             for line in fr:
#                 line = re.sub('\n', '', line)
#                 stoplist.append(line)
#             texts = [[word for word in document.split() if word not in stoplist]
#                      for document in list_cut]
#
#             # #去掉只出现一次的单词
#             frequency = defaultdict(int)
#             for text in texts:
#                 for token in text:
#                     frequency[token] += 1
#             texts = [[token for token in text if frequency[token] > 1]
#                      for text in texts]
#             dictionarygl = corpora.Dictionary(texts)
#             dictiongl = dictionarygl.token2id
#
#             corpus = [dictionarygl.doc2bow(text) for text in texts]
#
#             tfidf_model = models.TfidfModel(corpus)
#             tfidf = tfidf_model[corpus]
#             lista = []
#             listw = []
#             nodes = []
#             edges = []
#             nodedic = {}
#             for i in tfidf:
#                 temp = []
#                 i = sorted(i, key=lambda x: x[1], reverse=True)
#                 temp = i[0:6]
#
#                 for k, v in dictiongl.items():
#                     for j in range(len(temp)):
#                         temp[j] = list(temp[j])
#                         if temp[j][0] == v:
#                             temp[j][0] = k
#                 lista.append([x[0] for x in temp])
#                 listw.extend([x[0] for x in temp])
#
#             counts = dict(Counter(listw).most_common(int(val1)))
#             maxnum = Counter(listw).most_common(int(val1))[0][1]
#             num = 0
#             for k, v in counts.items():
#                 tdict = {}
#                 tdict['name'] = k
#                 tdict['value'] = v
#                 nodes.append(tdict)
#                 nodedic[k] = num
#                 num += 1
#             # print nodedic
#             matx = zeros((len(nodedic), len(nodedic)))
#             # print keylistAll
#             for k, v in nodedic.items():
#                 for m in lista:
#                     for mi in range(len(m)):
#                         if m[mi] == k:
#                             m[mi] = v
#
#             kk = 0
#             for keyInx in lista:
#                 combine = itertools.combinations(keyInx, 2)
#                 for j in combine:
#                     j = sorted(j)
#                     try:
#                         matx[j[0]][j[1]] += 1
#                     except:
#                         kk += 1
#
#             try:
#                 maxco = amax(matx)
#             except:
#                 maxco = 0
#
#             for i in range(len(nodedic)):
#                 for j in range(len(nodedic)):
#                     edict = {}
#
#                     if matx[i][j] != 0 and matx[i][j] >= int(val):
#                         edict['source'] = i
#                         edict['target'] = j
#                         edict['value'] = matx[i][j]
#                         edges.append(edict)
#
#     return render_to_response('himalaya/keywords_b.html',{'nodes': json.dumps(nodes), 'edges': json.dumps(edges),'maxnum': maxnum,'maxco':maxco})
#
#
# def base_cluster(request):
#     query = request.session.get('qq')
#     ret_num = request.session.get('ret_num')
#     queryb = request.session.get('queryb')
#     choiceitems1 = request.session.get('earlychoiceitems1')
#
#     advanceb = []
#     temp = []
#     advanceb.append(query)
#     for q in queryb:
#         if (q[0] == u'language' or q[0] == u'creator' or q[0] == u'fileType' or q[0] == u'inp_start_date' or q[
#             0] == u'keywords' or q[0] == u'title' or q[0] == u'inp_end_date'
#             or q[0] == u'fileFormat' or q[0] == u'spatial' or q[0] == u'discipline') and q[1] != [u'']:
#             temp.append(q[1])
#     for u in temp:
#         for uu in u:
#             advanceb.append(uu)
#     for m in choiceitems1:
#         advanceb.append(m[1])
#     advanceb = filter(lambda x: str(x) != '', advanceb)
#
#     list_class = range(1, 11)
#
#     return render(request, 'himalaya/base_cluster.html',{'list_class':list_class,'query': query, 'ret_num': ret_num, 'advanceb': advanceb})
#
# def cluster_b(request):
#     keyall = []
#     listr = []
#     listb_keywords = request.session.get('listb_keywords')
#     listb_abstract = request.session.get('listb_abstract')
#     val = 5
#     if request.GET.has_key('cb'):
#         if request.GET['cb']:
#             val = request.GET['cb']
#
#     if listb_keywords == [None] and listb_abstract == [None]:
#         qk = FileBaseInfo.objects.filter(subjecttype=-1).values_list('keywords')
#         qk = filter(lambda x: x[0] != None and x[0] != u'None' and x[0] != u'', qk)
#         listb_keywords = [i[0] for i in qk]
#         if listb_keywords == []:
#             qa = FileBaseInfo.objects.all().values_list('description')
#             qa = filter(lambda x: x[0] != None and x[0] != u'None' and x[0] != u'', qa)
#             listb_abstract = [i[0] for i in qa]
#
#     if len(listb_keywords) != 0:
#         for keyword in listb_keywords:
#             keyword = keyword.replace('HimalayaMountain', 'Himalaya Mountain')
#             keyword = keyword.replace('&', ';')
#             keyword = keyword.replace('--', ';')
#             keyword = keyword.replace('；', ';')
#             keyword = keyword.replace(',', ';')
#             keylist = keyword.split(';')
#
#             for v in range(len(keylist)):
#                 keylist[v] = keylist[v].strip()
#                 keylist[v] = re.sub('[0,9]*:', '', keylist[v])
#                 if keylist[v] != u'':
#                     keyall.append(keylist[v])
#         token_num = len(Counter(keyall))
#         if token_num > 35:
#             topN = 35
#         else:
#             topN = token_num
#         counts = dict(Counter(keyall).most_common(topN))
#         num_clusters = int(val)
#         if len(counts) > num_clusters:
#             key = []
#             for k in counts:
#                 k = k.lower()
#                 key.append(k)
#             nlp = spacy.load('en')
#             listvec = []
#             for keyw in key:
#                 test_doc = nlp(keyw)
#                 vec = zeros(300)
#                 for token in test_doc:
#                     vec += token.vector
#                 listvec.append(vec)
#
#             km_cluster = KMeans(n_clusters=num_clusters, max_iter=500, n_init=40, init='k-means++', n_jobs=1)
#             km_result = km_cluster.fit_predict(listvec)
#             index = zip(km_result, key)
#             result = defaultdict(list)
#             for i, j in index:
#                 result[i].append(j)
#
#             for k, v in result.items():
#                 dictr = {}
#                 dictr['name'] = 'class ' + str(k)
#                 dictr['y'] = len(v)
#                 dictr['Keywords'] = '; '.join(v)
#                 listr.append(dictr)
#     elif len(listb_abstract) != 0:
#         new_model = gensim.models.KeyedVectors.load_word2vec_format('wiki.zh.text.vector.bin', binary=True)
#         list_cut = []
#         jieba.load_userdict("dict/userdict.txt")
#         for abstract in listb_abstract:
#             abstract = abstract.replace('\xe2\x80\xa2', '_')
#             abstract = abstract.replace('\xc2\xb7', '_')
#             abstract = abstract.replace('-', '_')
#             fenci = jieba.cut(abstract)
#             fenci = list(fenci)
#             fenci2 = [x for x in fenci if len(x) > 1]
#             fencis = ' '.join(fenci2)
#             fencis = re.sub("_", "\xc2\xb7".decode('utf-8'), fencis)
#             list_cut.append(fencis)
#
#         stoplist = []
#         with open('dict/ch_stopword.txt', 'r') as fr:
#             for line in fr:
#                 line = re.sub('\n', '', line)
#                 stoplist.append(line)
#             texts = [[word for word in document.split() if word not in stoplist]
#                      for document in list_cut]
#
#             # 去掉只出现一次的单词
#             frequency = defaultdict(int)
#             for text in texts:
#                 for token in text:
#                     frequency[token] += 1
#             texts = [[token for token in text if frequency[token] > 1]
#                      for text in texts]
#             dictionary = corpora.Dictionary(texts)
#             diction = dictionary.token2id
#             corpus = [dictionary.doc2bow(text) for text in texts]
#
#             tfidf_model = models.TfidfModel(corpus)
#             tfidf = tfidf_model[corpus]
#             listw = []
#             for i in tfidf:
#                 temp = []
#                 if len(i) != 0:
#                     i = sorted(i, key=lambda x: x[1], reverse=True)
#                     temp = i[0:6]
#                     for k, v in diction.items():
#                         for j in range(len(temp)):
#                             temp[j] = list(temp[j])
#                             if temp[j][0] == v:
#                                 temp[j][0] = k
#
#                 listw.extend([x[0] for x in temp])
#
#             token_num = len(Counter(listw))
#             if token_num > 35:
#                 topN = 35
#             else:
#                 topN = token_num
#             count = dict(Counter(listw).most_common(topN))
#             alist = []
#             wlist = []
#             error = []
#             for word in count:
#                 try:
#                     vector = new_model[word]
#                     wlist.append(word)
#                     alist.append(vector)
#                 except:
#                     error.append(word)
#
#         num_clusters = int(val)
#         km_cluster = KMeans(n_clusters=num_clusters, max_iter=500, n_init=40, init='k-means++', n_jobs=1)
#         km_result = km_cluster.fit_predict(alist)
#         index = zip(km_result, wlist)
#         result = defaultdict(list)
#         for i, j in index:
#             result[i].append(j)
#         # listr = []
#         for k, v in result.items():
#             dictr = {}
#             dictr['name'] = 'class ' + str(k)
#             dictr['y'] = len(v)
#             dictr['Keywords'] = '; '.join(v)
#             listr.append(dictr)
#     return render_to_response('himalaya/cluster_b.html',{'listr':json.dumps(listr),'listr2':listr})
# def base_cocreator(request):
#     query = request.session.get('qq')
#     ret_num = request.session.get('ret_num')
#     queryb = request.session.get('queryb')
#     choiceitems1 = request.session.get('earlychoiceitems1')
#     # print 'hthththththth',listb_creator
#     advanceb = []
#     temp = []
#
#     advanceb.append(query)
#     for q in queryb:
#         if (q[0] == u'language' or q[0] == u'creator' or q[0] == u'fileType' or q[0] == u'inp_start_date' or q[
#             0] == u'keywords' or q[0] == u'title' or q[0] == u'inp_end_date'
#             or q[0] == u'fileFormat' or q[0] == u'spatial' or q[0] == u'discipline') and q[1] != [u'']:
#             temp.append(q[1])
#     for u in temp:
#         for uu in u:
#             advanceb.append(uu)
#     for m in choiceitems1:
#         advanceb.append(m[1])
#     advanceb = filter(lambda x: str(x) != '', advanceb)
#     list_cre = range(1,51)
#
#     return render(request, 'himalaya/base_cocreator.html', {'list_cre':list_cre,
#                                                            'query': query, 'ret_num': ret_num, 'advanceb': advanceb,
#                                                            })
#
# def creator_b(request):
#     listb_creator = request.session.get('listb_creator')
#     val = 30
#     if request.GET.has_key('numcb'):
#         if request.GET['numcb']:
#             val = request.GET['numcb']
#
#     list = []
#     listco = []
#     nodes = []
#     edges = []
#     maxnum = 0
#     maxco = 0
#     nodedic = {}
#     if listb_creator == [None]:
#         qk = FileBaseInfo.objects.filter(subjecttype=-1).values_list('creator')
#         qk = filter(lambda x: x[0] != None and x[0] != u'None' and x[0] != u'', qk)
#         listb_creator = [i[0] for i in qk]
#     if len(listb_creator) != 0:
#         for creator in listb_creator:
#             creators = creator.split(';')
#             creators = filter(lambda x: x != None and x != u'Anonymous' and x != u' et al', creators)
#             for i in range(len(creators)):
#                 creators[i] = creators[i].title()
#                 creators[i] = re.sub('-', ' ', creators[i])
#                 creators[i] = creators[i].strip()
#                 if creators[i].__contains__('\n'):
#                     creators[i] = creators[i].split('\n')[0]
#                 list.append(creators[i])
#             if len(creators) != 0:
#                 listco.append(creators)
#
#         counts = dict(Counter(list).most_common(int(val)))
#         maxnum = Counter(list).most_common(int(val))[0][1]
#         # print len(dict(Counter(list)))
#         # SortCounts = sorted(counts.items(), key=lambda a:a[1],reverse=True)
#
#         num = 0
#         for k, v in counts.items():
#             tdict = {}
#             tdict['name'] = k
#             tdict['value'] = v
#             nodes.append(tdict)
#             nodedic[k] = num
#             num += 1
#
#         matx = zeros((len(nodedic), len(nodedic)))
#
#         for m in listco:
#             for mi in range(len(m)):
#                 for k, v in nodedic.items():
#                     if m[mi] == k:
#                         m[mi] = v
#         kk = 0
#         for keyInx in listco:
#             combine = itertools.combinations(keyInx, 2)
#             for j in combine:
#                 j = sorted(j)
#                 try:
#                     matx[j[0]][j[1]] += 1
#                 except:
#                     kk += 1
#         try:
#             maxco = amax(matx)
#         except:
#             maxco = 0
#         for i in range(len(nodedic)):
#             for j in range(len(nodedic)):
#                 edict = {}
#                 if matx[i][j] > 0:
#                     edict['source'] = i
#                     edict['target'] = j
#                     edict['value'] = matx[i][j]
#                     edges.append(edict)
#
#     return render_to_response('himalaya/creator_b.html',{'nodes': json.dumps(nodes), 'edges': json.dumps(edges),'maxnum': maxnum,'maxco':maxco})
#
#
#
# def full_keywords(request):
#     query = request.session.get('qq')
#     ret_num = request.session.get('ret_num')
#     queryf = request.session.get('queryf')
#     choiceitems2 = request.session.get('earlychoiceitems2')
#     advancef = []
#     temp = []
#     advancef.append(query)
#     for q in queryf:
#         if (q[0] == u'language' or q[0] == u'creator' or q[0] == u'fileType' or q[0] == u'inp_start_date' or q[
#             0] == u'keywords' or q[0] == u'title' or q[0] == u'inp_end_date'
#             or q[0] == u'fileFormat' or q[0] == u'spatial' or q[0] == u'discipline') and q[1] != [u'']:
#             temp.append(q[1])
#
#     for u in temp:
#         for uu in u:
#             advancef.append(uu)
#
#     for m in choiceitems2:
#         advancef.append(m[1])
#
#     advancef = filter(lambda x: str(x) != '', advancef)
#     list_coN = range(1, 31)
#     list_num = range(10, 51)
#     return render(request, 'himalaya/full_keywords.html', {'list_coN': list_coN, 'list_num': list_num,
#                                                            'query': query, 'ret_num': ret_num, 'advancef': advancef,
#                                                            })
# def keyword_f(request):
#     listf_keywords = request.session.get('listf_keywords')
#     listf_abstract = request.session.get('listf_abstract')
#     val = 5
#     val1 = 50
#     if request.GET.has_key('fullc'):
#         if request.GET['fullc']:
#             val = request.GET['fullc']
#     if request.GET.has_key('numf'):
#         if request.GET['numf']:
#             val1 = request.GET['numf']
#
#     keyall = []
#     keylistAll = []
#     nodedic = {}
#     nodes = []
#     edges = []
#     maxnum = 0
#     maxco = 0
#
#     if listf_keywords == [None] and listf_abstract == [None]:
#         qk = FileBaseInfo.objects.all().values_list('keywords')
#         qk = filter(lambda x: x[0] != None and x[0] != u'None' and x[0] != u'', qk)
#         listf_keywords = [i[0] for i in qk]
#         if listf_keywords == []:
#             qa = FileBaseInfo.objects.all().values_list('description')
#             qa = filter(lambda x: x[0] != None and x[0] != u'None' and x[0] != u'', qa)
#             listf_abstract = [i[0] for i in qa]
#
#     if len(listf_keywords) != 0:
#         for keyword in listf_keywords:
#             keyword = keyword.replace('HimalayaMountain', 'Himalaya Mountain')
#             keyword = keyword.replace('\xe2\x80\xa2', '\xc2\xb7')
#             keyword = keyword.replace('--', ';')
#             keyword = keyword.replace(',', ';')
#             keyword = keyword.replace('&', ';')
#             keyword = keyword.replace('；', ';')
#             keylist = keyword.split(';')
#
#             for v in range(len(keylist)):
#                 keylist[v] = keylist[v].strip()
#                 keylist[v] = re.sub('[0,9]*:', '', keylist[v])
#                 if keylist[v] != u'':
#                     keyall.append(keylist[v])
#
#             keylistAll.append(keylist)
#         # print keyall
#
#         counts = dict(Counter(keyall).most_common(int(val1)))
#         maxnum = Counter(keyall).most_common(int(val1))[0][1]
#
#         # print 'ccc',counts
#         num = 0
#         for k, v in counts.items():
#             tdict = {}
#             tdict['name'] = k
#             tdict['value'] = v
#             nodes.append(tdict)
#             nodedic[k] = num
#             num += 1
#         matx = zeros((len(nodedic), len(nodedic)))
#         for k, v in nodedic.items():
#             for m in keylistAll:
#                 for mi in range(len(m)):
#                     if m[mi] == k:
#                         m[mi] = v
#         kk = 0
#         for keyInx in keylistAll:
#             combine = itertools.combinations(keyInx, 2)
#             for j in combine:
#                 j = sorted(j)
#                 try:
#                     matx[j[0]][j[1]] += 1
#                 except:
#                     kk += 1
#         try:
#             maxco = amax(matx)
#         except:
#             maxco = 0
#
#         for i in range(len(nodedic)):
#             for j in range(len(nodedic)):
#                 edict = {}
#                 if matx[i][j] != 0 and matx[i][j] >= int(val):
#                     edict['source'] = i
#                     edict['target'] = j
#                     edict['value'] = matx[i][j]
#                     edges.append(edict)
#     elif len(listf_abstract) != 0:
#         list_cut = []
#         jieba.load_userdict("dict/userdict.txt")
#         for abstract in listf_abstract:
#             abstract = abstract.replace('\xe2\x80\xa2', '_')
#             abstract = abstract.replace('\xc2\xb7', '_')
#             abstract = abstract.replace('-', '_')
#             fenci = jieba.cut(abstract)
#             fenci = list(fenci)
#             fenci2 = [x for x in fenci if len(x) > 1]
#             fencis = ' '.join(fenci2)
#             fencis = re.sub("_", "\xc2\xb7".decode('utf-8'), fencis)
#             list_cut.append(fencis)
#
#         stoplist = []
#         with open('dict/ch_stopword.txt', 'r') as fr:
#             for line in fr:
#                 line = re.sub('\n', '', line)
#                 stoplist.append(line)
#             texts = [[word for word in document.split() if word not in stoplist]
#                      for document in list_cut]
#
#             # #去掉只出现一次的单词
#             frequency = defaultdict(int)
#             for text in texts:
#                 for token in text:
#                     frequency[token] += 1
#             texts = [[token for token in text if frequency[token] > 1]
#                      for text in texts]
#             dictionarygl = corpora.Dictionary(texts)
#             dictiongl = dictionarygl.token2id
#
#             corpus = [dictionarygl.doc2bow(text) for text in texts]
#
#             tfidf_model = models.TfidfModel(corpus)
#             tfidf = tfidf_model[corpus]
#             lista = []
#             listw = []
#             nodes = []
#             edges = []
#             nodedic = {}
#             for i in tfidf:
#                 temp = []
#                 i = sorted(i, key=lambda x: x[1], reverse=True)
#                 temp = i[0:6]
#
#                 for k, v in dictiongl.items():
#                     for j in range(len(temp)):
#                         temp[j] = list(temp[j])
#                         if temp[j][0] == v:
#                             temp[j][0] = k
#                 lista.append([x[0] for x in temp])
#                 listw.extend([x[0] for x in temp])
#
#             counts = dict(Counter(listw).most_common(int(val1)))
#             maxnum = Counter(listw).most_common(int(val1))[0][1]
#
#             num = 0
#             for k, v in counts.items():
#                 tdict = {}
#                 tdict['name'] = k
#                 tdict['value'] = v
#                 nodes.append(tdict)
#                 nodedic[k] = num
#                 num += 1
#             matx = zeros((len(nodedic), len(nodedic)))
#             for k, v in nodedic.items():
#                 for m in lista:
#                     for mi in range(len(m)):
#                         if m[mi] == k:
#                             m[mi] = v
#
#             kk = 0
#             for keyInx in lista:
#                 combine = itertools.combinations(keyInx, 2)
#                 for j in combine:
#                     j = sorted(j)
#                     try:
#                         matx[j[0]][j[1]] += 1
#                     except:
#                         kk += 1
#
#             try:
#                 maxco = amax(matx)
#             except:
#                 maxco = 0
#
#             for i in range(len(nodedic)):
#                 for j in range(len(nodedic)):
#                     edict = {}
#                     if matx[i][j] != 0 and matx[i][j] >= int(val):
#                         edict['source'] = i
#                         edict['target'] = j
#                         edict['value'] = matx[i][j]
#                         edges.append(edict)
#     return render_to_response('himalaya/keyword_f.html',{'nodes': json.dumps(nodes), 'edges': json.dumps(edges),'maxco':maxco,'maxnum':maxnum})
#

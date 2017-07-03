# coding=utf-8
import json
import operator
from collections import Counter
from datetime import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext
from haystack.query import SearchQuerySet

from .models import BookList, Route, Site, TravelData


# Create your tests here.
def timerange(request):
    print 'timerange'
    rangetime='1900,2017'
    if request.GET.has_key('range'):
        rangetime=request.GET['range']
        print 'zz',rangetime
    return render_to_response('himalaya/timerange.html/', {'rangetime':rangetime}, context_instance=RequestContext(request))


#地图test start
#百度地图 先留着 以后要删 ( 以及包括 position.html 和 showLoc.html到时直接删) start
def position(request):
    print 'position'
    if request.method == 'POST':
        # 获取地址字符串 eg.西藏自治区, 阿里地区, 改则县,83.870984,31.998224
       dizhi=request.POST['dizhi']
       print dizhi
        # 分割地址字符串为数组
       dizhi=dizhi.split(u',')
       for item in dizhi:
           print item
       # 获取地址定位坐标（lon,lat）（83.870984,31.998224）
       lon=dizhi[-2]
       lat = dizhi[-1]
       print 'lon,lat',lon,lat
    return render_to_response('himalaya/position.html',context_instance=RequestContext(request))

def example(request):
    print 'example'
    return render_to_response('himalaya/example/example.html',context_instance=RequestContext(request))
#百度地图 先留着 以后要删 end


#QGIS2WEB

def maptest(request):
    print 'maptest'


    return render_to_response('himalaya/maptest.html/', context_instance=RequestContext(request))
#地图test end



#游历数据库专栏展示页
def mapview(request):
    print 'mapview'

    return render_to_response('himalaya/mapview.html/', context_instance=RequestContext(request))


def gis_show(request):
    print 'gis_show'
    print ' 初始默认'

    triplist = []
    tripitemlist=[]
    linelist=[]
    routenamelist=[]
    all_impRecorsd=[]
    all_routeRecorsds=[]
    #nonecheck用来检测是否搜索全为空
    nonecheck=1
    #check 和 count 是关于前台 检索书目的显示
    check=''
    count=0
    # 模糊搜索(在solr里把filed设为对应的textsimple)
    if request.GET.has_key('bookname'):
        if request.GET['bookname']:
            nonecheck = 0
            print '——————————————————————————————书名 模糊搜索————————————————————————————————'
            bookname=request.GET['bookname']
            bookname_resultsch = SearchQuerySet().models(BookList).filter(bNameCH=bookname)|\
                                 SearchQuerySet().models(BookList).filter(bNameEN=bookname)
            print '搜索的书目词：',bookname
            print '该搜索词模糊匹配书目的结果数（bookname_resultsCH）：',bookname_resultsch.count()
            for info in bookname_resultsch:
                print 'item',info.object.bookID
                print '书名',info.bNameCH
                bookname_result = SearchQuerySet().models(Route).filter(bookID=info.object.bookID)
                print  '该书目有游历路线count：', bookname_result.count(), '条'
                if bookname_result.count():
                    for item in bookname_result:
                        print 'bookname test:', item.object.id
                        all_impRecorsd.append((1,item.object.id))
                        all_routeRecorsds.append(item.object.id)
                else:
                    all_impRecorsd.append((1, -1))
            print '——————————————————————————————书名 模糊搜索————————————————————————————————'

    if request.GET.has_key('people'):
        if request.GET['people']:
            nonecheck = 0
            print '——————————————————————————————人名 模糊搜索————————————————————————————————'
            people = request.GET['people']
            people_results = SearchQuerySet().models(Route).filter(RoutePer=people)
            # print '搜索的人名词：', people
            print '该搜索词模糊匹配人名的结果数（people_resultsch）：', people_results.count()
            if people_results.count():
                for item in people_results:
                    print 'people test:', item.object.id
                    all_impRecorsd.append((2, item.object.id))
                    all_routeRecorsds.append(item.object.id)
            else:
                all_impRecorsd.append((2, -1))
            print '——————————————————————————————人名 模糊搜索————————————————————————————————'

    if request.GET.has_key('routename'):
        if request.GET['routename']:
            nonecheck = 0
            print '——————————————————————————————游历路线名 模糊搜索————————————————————————————————'
            routename = request.GET['routename']
            routename_results = SearchQuerySet().models(Route).filter(RouteName=routename)
            # print '搜索的游历路线词：', routename
            print '该搜索词模糊匹配游历路线词的结果数（routename_results）：', routename_results.count()
            if routename_results.count():
                for item in routename_results:
                    print 'routename test:', item.object.id
                    all_impRecorsd.append((3, item.object.id))
                    all_routeRecorsds.append(item.object.id)
            else:
                all_impRecorsd.append((3, -1))
            print '——————————————————————————————游历路线名 模糊搜索————————————————————————————————'

    if request.GET.has_key('travelway'):
        if request.GET['travelway']:
            nonecheck = 0
            print '——————————————————————————————交通方式 模糊搜索 有存wayorder————————————————————————————————'
            travelway=request.GET['travelway']
            travelway_results = SearchQuerySet().models(TravelData).filter(transportation=travelway)

            print '搜索的交通方式词：',travelway
            print  '该交通方式有游历路线count(这里会有重复！！！！！！！)：', travelway_results.count(), '条'

            # 路线去重，因为有的路线可能存在多种该交通方式  并记录交通方式对应地点的路线order start
            if travelway_results.count():
                for item in travelway_results:
                    print 'travelway test:',item.object.RouteName,item.object.RouteName.id,item.object.order,item
                    all_impRecorsd.append((4,item.object.RouteName.id))
                    all_routeRecorsds.append(item.object.RouteName.id)
            else:
                all_impRecorsd.append((4, -1))
            print '——————————————————————————————交通方式 模糊搜索————————————————————————————————'

    if request.GET.has_key('opinion'):
        if request.GET['opinion']:
            nonecheck = 0
            print '——————————————————————————————所见所闻 模糊搜索 有存wayorder————————————————————————————————'
            opinion = request.GET['opinion']
            opinion_results = SearchQuerySet().models(TravelData).filter(nation=opinion)|\
                              SearchQuerySet().models(TravelData).filter(police=opinion)|\
                              SearchQuerySet().models(TravelData).filter(economy=opinion)|\
                              SearchQuerySet().models(TravelData).filter(agriculture=opinion)|\
                              SearchQuerySet().models(TravelData).filter(religion=opinion)|\
                              SearchQuerySet().models(TravelData).filter(history=opinion) |\
                              SearchQuerySet().models(TravelData).filter(education=opinion) |\
                              SearchQuerySet().models(TravelData).filter(religion=opinion) |\
                              SearchQuerySet().models(TravelData).filter(geography=opinion) |\
                              SearchQuerySet().models(TravelData).filter(other=opinion)
                # print '搜索的游历路线词：', routename
            print '该搜索词模糊匹配游历路线词的结果数（ opinion_results）：', opinion_results.count()

            # 路线去重，因为有的路线可能存在多种该查询词  并记录交通方式对应地点的路线order start
            if opinion_results.count():
                for item in  opinion_results:
                    # print ' opinion test(存在可能相同路线不同地点order下有相同的见闻):', item.object.RouteName, item.object.RouteName.id, item.object.order, item
                    all_impRecorsd.append((5, item.object.RouteName.id))
                    all_routeRecorsds.append(item.object.RouteName.id)
            else:
                all_impRecorsd.append((5, -1))
            print '——————————————————————————————所见所闻 模糊搜索————————————————————————————————'

    if request.GET.has_key('routelocation'):
        if request.GET['routelocation']:
            nonecheck = 0
            print '——————————————————————————————地名 精确匹配 有存wayorder————————————————————————————————'
            routelocation= request.GET['routelocation']
            routelocation_results = SearchQuerySet().models(Site).filter(sitenameCH =routelocation)| \
                                SearchQuerySet().models(Site).filter(siteNameEN =routelocation)
            # print '搜索的游历路线词：', routename
            print '该搜索词模糊匹配地名的结果数（routename_results）：', routelocation_results.count()
            if routelocation_results.count():
                for item in routelocation_results:
                    print '地名在Site表里对应的id：',item.object.id
                    results=SearchQuerySet().models(TravelData).filter(siteid =item.object.id)
                    for siteitem in results:
                        print 'sitesearch:',siteitem.object.RouteName,siteitem.object.RouteName.id
                        all_impRecorsd.append((6,siteitem.object.RouteName.id))
                        all_routeRecorsds.append(siteitem.object.RouteName.id)
            else:
                all_impRecorsd.append((6, -1))
            print '——————————————————————————————地名 精确匹配————————————————————————————————'

    if request.GET.has_key('add_date'):
        if request.GET['add_date']:
            nonecheck = 0
            print '——————————————————————————————时间段 搜索开始 有存wayorder————————————————————————————————'
            routetime=request.GET['add_date']
            print '搜索的交通方式词：', routetime
            #转换为时间类型
            aa = routetime.split('-')
            s_t = datetime.strptime(''.join(aa), "%Y%m%d").date()
            routetime_results = SearchQuerySet().models(TravelData).filter(tol__gte=s_t)
            routetime_results=routetime_results.models(TravelData).filter(toa__lte=s_t)
            print  '该交通方式有游历路线count(这里会有重复！！！！！！！)：', routetime_results.count(), '条'
            # for item in routetime_results:
            #     print '结果 路线id,路线中该记录order,起始时间,离开时间：',item.object.RouteName, item.object.order,item.object.toa, item.object.tol
            # 路线去重，因为有的路线可能存在多种该交通方式  并记录交通方式对应地点的路线order start
            if routetime_results.count():
                for item in routetime_results:
                    print 'testtest:',item.object.RouteName,item.object.RouteName.id,item.object.order,item
                    all_impRecorsd.append((7, item.object.RouteName.id))
                    all_routeRecorsds.append(item.object.RouteName.id)
            else:
                all_impRecorsd.append((7, -1))
            print '——————————————————————————————时间段 搜索结束————————————————————————————————'

    # print '################################################'
    # print 'all_impRecorsd (没有去重的)：',len(all_impRecorsd)
    # print 'all_impRecorsd',all_impRecorsd
    # for item in all_impRecorsd:
    #     print 'item',item
    # #
    # print 'all_routeRecorsds（只有routeid）(没有去重的)路线个数：',len(all_routeRecorsds)
    # print 'all_routeRecorsds',all_routeRecorsds
    # print '################################################'
    #--------------总搜索 全部搜索合并后并去重！！！！！！！！！！-----------------------
    #searchcheck检测点击了搜索按钮
    searchcheck=0
    if request.GET.has_key('mapq'):
        print '全搜索'
        searchcheck = 1
        check = 1
        routeset = list(set(all_routeRecorsds))
        if len(routeset):
            triplist = []
            tripitemlist = []
            linelist=[]
            triplist, tripitemlist,linelist = traveldatasearchloglat(routeset, triplist, tripitemlist,linelist)
            routenamelist = routenameitem(routeset)
            count = len(triplist)


    if request.GET.has_key('checkthis'):
        print '高级搜索'
        searchcheck = 1
        check = 1
        checklist=[]
        zz=[]
        final=[]
        if len(all_impRecorsd):
            oo = all_impRecorsd[0][0]
            for item in all_impRecorsd:
                if item[0]==oo:
                    zz.append(item[1])
                else:
                    checklist.append(zz)
                    zz = []
                    zz.append(item[1])
                    oo=item[0]
            checklist.append(zz)
            print 'checklist',checklist
            print len(checklist)
            if len(checklist):
                #高级搜索要求各类搜索的交集 start
                if len(checklist)>2:
                    # print '2以上'
                    dd = checklist[0]
                    for num in range(0,len(checklist)-2):
                        final=list(set(dd).intersection(set(checklist[num+1])))
                        dd=final
                        # print 'final1',final
                if len(checklist)==2:
                    # print '=2'
                    final = list(set(checklist[0]).intersection(set(checklist[1])))
                    # print 'final2', final
                # 高级搜索要求各类搜索的交集 end
                if len(checklist) == 1:
                    # print '只有一项搜索'
                    final=list(set(checklist[0]))
                    # print 'final3', final
            #高级搜索 最后得到 routeid 集为final
            triplist = []
            tripitemlist = []
            linelist=[]
            # print 'final',final
            if -1 not in final:
                routenamelist = routenameitem(final)
                triplist, tripitemlist,linelist = traveldatasearchloglat(final, triplist, tripitemlist,linelist)
            count = len(triplist)
    #搜空的时候显示全部
    if searchcheck and nonecheck:
        print '任何搜索 空'
        routeset=[]
        allset=Route.objects.all()
        print 'allset',allset.count()
        for item in allset:
            print item.id
            routeset.append(item.id)
        # print 'routeset', routeset
        routenamelist = routenameitem(routeset)
        triplist, tripitemlist,linelist = traveldatasearchloglat(routeset, triplist, tripitemlist,linelist)
        count = len(triplist)


    print '——————————————————————————————最终搜索结果————————————————————————————————'

    print 'triplist:', len(triplist),triplist
    print 'tripitemlist:', len(tripitemlist)
    print 'routenamelist',len(routenamelist)
    print 'count',count

    for item in triplist:
        print item

    return render_to_response('himalaya/travel/gis_show.html/', {'count':count,'check':check,'routenamelist':json.dumps(routenamelist),'triplist':json.dumps(triplist),'linelist':json.dumps(linelist),'tripitemlist':json.dumps(tripitemlist)},context_instance=RequestContext(request))


def route_map(request):
    print 'route_map'
    return render_to_response('himalaya/travel/routemap.html/', context_instance=RequestContext(request))


#Map 功能函数 定义 start
def delorder(list):
    num = 0
    for i in list:
        del list[num][0]
        num += 1
    # print list
    return list

def traveldatasearchloglat(results,triplist,tripitemlist,linelist):

    # 先记录重复路过的地点id start
    checksiteidlist=[]
    checksiteid = []
    for itemzz in results:
        for tmp in TravelData.objects.filter(RouteName=itemzz):
            checksiteid.append(tmp.siteid.id)
    checksiteid = Counter(checksiteid)
    for k, v in checksiteid.items():
        if v > 1:
            checksiteidlist.append(k)
    # print 'checksiteidlist', checksiteidlist
    # 先记录重复路过的地点id end
    repeatitem=['']*len(checksiteidlist)

    point = 0.001
    for item in results:
        trip = []
        tripitem = []
        linezz=[]
        for tmp in TravelData.objects.filter(RouteName=item):
            content = []
            sitelist = []
            line=[]
            # num=checksiteidlist.index(tmp.siteid.id)
            if tmp.siteid.id in checksiteidlist:

                content.append(tmp.order)
                content.append(tmp.siteid.sitenameCH)
                content.append(tmp.siteid.sitenameEN)
                # content.append(int(tmp.order)+1)
                order = int(tmp.order) + 1
                jianwen = ''
                jianwen = jianwen + '<span style="color:#9c4646;font-weight:bold;">所属游历路线： ' + tmp.RouteName.RouteName + '</span><br>'
                jianwen = jianwen + '<span style="font-weight:bold;">所属路线的第  ' + str(order) + '  站</span><br>'
                if tmp.transportation:
                    jianwen = jianwen + '<span style="font-weight:bold;">交通方式： </span>' + tmp.transportation + '<br>'
                if str(tmp.toa):
                    jianwen = jianwen + '<span style="font-weight:bold;">抵达时间： </span>' + str(tmp.toa) + '<br>'
                if str(tmp.tol):
                    jianwen = jianwen + '<span style="font-weight:bold;">离开时间： </span>' + str(tmp.tol) + '<br>'
                if tmp.police:
                    jianwen = jianwen + '<span style="font-weight:bold;">政治/军事： </span>' + tmp.police + '<br>'
                if tmp.economy:
                    jianwen = jianwen + '<span style="font-weight:bold;">商贸经济： </span>' + tmp.economy + '<br>'
                if tmp.custom:
                    jianwen = jianwen + '<span style="font-weight:bold;">风俗文化： </span>' + tmp.custom + '<br>'
                if tmp.agriculture:
                    jianwen = jianwen + '<span style="font-weight:bold;">农业： </span>' + tmp.agriculture + '<br>'
                if tmp.history:
                    jianwen = jianwen + '<span style="font-weight:bold;">历史： </span>' + tmp.history + '<br>'
                if tmp.education:
                    jianwen = jianwen + '<span style="font-weight:bold;">教育： </span>' + tmp.education + '<br>'
                if tmp.geography:
                    jianwen = jianwen + '<span style="font-weight:bold;">自然地理/灾害： </span>' + tmp.geography + '<br>'
                if tmp.religion:
                    jianwen = jianwen + '<span style="font-weight:bold;">宗教： </span>' + tmp.religion + '<br>'
                if tmp.nation:
                    jianwen = jianwen + '<span style="font-weight:bold;">人口/民族: </span>' + tmp.nation + '<br>'
                if tmp.other:
                    jianwen = jianwen + '<span style="font-weight:bold;">其他: </span>' + tmp.other


                indexnum=checksiteidlist.index(tmp.siteid.id)
                # print 'repeat:',tmp.siteid.id,checksiteidlist.index(tmp.siteid.id)

                repeatitem[indexnum]=repeatitem[indexnum]+jianwen+'<HR align=left width=100% color=#999 SIZE=5 noShade>'

                # print ' 后台整理所见所闻：',jianwen
                content.append(repeatitem[indexnum])
                content.append(tmp.transportation)

                #为了linelist重复点错位画线 准备数据
                line.append(tmp.order)

                line.append(float(tmp.siteid.latitude)+point)
                line.append(float(tmp.siteid.longitude)+point)
                point+=0.001

            else:
                content.append(tmp.order)
                content.append(tmp.siteid.sitenameCH)
                content.append(tmp.siteid.sitenameEN)
                order=int(tmp.order)+1
                jianwen=''
                jianwen = jianwen + '<span style="color:#9c4646;font-weight:bold;">所属游历路线： ' + tmp.RouteName.RouteName+ '</span><br>'
                jianwen = jianwen + '<span style="font-weight:bold;">所属路线的第  ' + str(order) + '  站</span><br>'
                print tmp.transportation
                if tmp.transportation:
                    jianwen=jianwen+'<span style="font-weight:bold;">交通方式： </span>'+tmp.transportation+'<br>'
                if str(tmp.toa):
                    jianwen=jianwen+'<span style="font-weight:bold;">抵达时间： </span>'+str(tmp.toa)+'<br>'
                if str(tmp.tol):
                    jianwen=jianwen+'<span style="font-weight:bold;">离开时间： </span>'+str(tmp.tol)+'<br>'
                if tmp.police:
                    jianwen=jianwen+'<span style="font-weight:bold;">政治/军事： </span>'+tmp.police+'<br>'
                if tmp.economy:
                    jianwen=jianwen+'<span style="font-weight:bold;">商贸经济： </span>'+tmp.economy+'<br>'
                if tmp.agriculture:
                    jianwen=jianwen+'<span style="font-weight:bold;">农业： </span>'+tmp.agriculture+'<br>'
                if tmp.history:
                    jianwen=jianwen+'<span style="font-weight:bold;">历史： </span>'+tmp.history+'<br>'
                if tmp.education:
                    jianwen=jianwen+'<span style="font-weight:bold;">教育： </span>'+tmp.education+'<br>'
                if tmp.geography:
                    jianwen=jianwen+'<span style="font-weight:bold;">自然地理/灾害： </span>'+tmp.geography+'<br>'
                if tmp.religion:
                    jianwen=jianwen+'<span style="font-weight:bold;">宗教： </span>'+tmp.religion+'<br>'
                if tmp.nation:
                    jianwen=jianwen+'<span style="font-weight:bold;">人口/民族: </span>'+tmp.nation+'<br>'
                if tmp.other:
                    jianwen = jianwen + '<span style="font-weight:bold;">其他: </span>' + tmp.other
                # print ' 后台整理所见所闻：',jianwen
                content.append(jianwen)
                content.append(tmp.transportation)

                line.append(tmp.order)

                line.append(float(tmp.siteid.latitude))
                line.append(float(tmp.siteid.longitude))

            sitelist.append(tmp.order)

            sitelist.append(float(tmp.siteid.latitude))
            sitelist.append(float(tmp.siteid.longitude))


            # 目前主要传这两个列表（经纬度列表，content列表）
            tripitem.append(content)
            trip.append(sitelist)
            linezz.append(line)

        tripitem.sort(key=operator.itemgetter(0))
        tripitem = delorder(tripitem)

        trip.sort(key=operator.itemgetter(0))
        trip = delorder(trip)

        linezz.sort(key=operator.itemgetter(0))
        linezz = delorder(linezz)

        triplist.append(trip)
        tripitemlist.append(tripitem)
        linelist.append(linezz)

    # print 'repeatitem',repeatitem
    return triplist,tripitemlist,linelist

def routenameitem(final):
    print 'routenameitem'
    routeitem = []
    for i in final :
        result=Route.objects.filter(id=i)
        #  route表里根据id查找的结果只会有一个
        routeitem.append(result[0].RouteName)
    return routeitem

#Map 功能函数 定义 end


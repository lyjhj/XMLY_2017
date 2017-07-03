# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, HttpResponseRedirect, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from .models import *
from xadmin.sites import site
from xadmin.views import BaseAdminView, BaseAdminObject
from adminx import *
from .forms import *
import os, sys, time
import django.db.models
import zipfile
from django.template import RequestContext
from django.core.urlresolvers import reverse
from datetime import datetime
from django.db import connection, transaction
from django.contrib import messages
from .serializers import CategorySerializer
from rest_framework.renderers import JSONRenderer
from django_ajax.decorators import ajax
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import xlrd,chardet
import django.contrib.sessions.middleware
from django.apps import AppConfig
from django.apps import apps
from pyPdf import PdfFileWriter, PdfFileReader
import sys,re,glob
import random
import cPickle
from collections import OrderedDict
from haystack import signals
from os.path import getsize
from wand.image import Image
from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfgen import canvas
from  xlutils.copy import copy
import json
import shutil
#zsy添加
import pinyinconvert
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)




def get_choices():
    sf = ['基础文献']
    sfid = [-1]
    for i in range(0, len(Subject.objects.all())):
        sf.append(Subject.objects.all()[i].subjectName)
        sfid.append(Subject.objects.all()[i].id)
    level_choice = zip(sfid, sf)
    return level_choice


class ChoiceForm(forms.Form):
    choice = forms.ChoiceField(choices=get_choices(), label="",
                               initial='',
                               widget=forms.Select(),
                               required=True)


# 动态生成表单的所属专题subjectid
def getsubject(it,i):
    global level
    if(level<i): level = i
    if it==None:
        tmp = Subject.objects.filter(subParent=None)
    else:
        tmp = Subject.objects.filter(subParent = int(it.id))
    lis = []
    for item in tmp:
        data = dict()
        data['name'] = item.subjectName
        data['value'] = item.id
        if(Subject.objects.filter(subParent = int(item.id))):
            data['sub'] = getsubject(item,i+1)
        lis.append(data)
    return lis





def filechoiceadd(req):
    if req.method == 'POST':
        level = req.POST.get('level')
        level = range(0, len(level.split(',')))
        for i in level:
            tmpd = req.POST.get('level_' + str(len(level) - i - 1))
            if tmpd and Subject.objects.get(id=int(tmpd)).hasChild==False:
                if(int(tmpd) == -1):
                    dynamicsubjectid = 0
                else:
                    dynamicsubjectid = int(tmpd)
            # 跳转正确的界面
                global username
                username=req.user
                if(req.POST.get("select")=='swf'):
                    return redirect(r"../swfupload/"+str(dynamicsubjectid))
                else:
                    return redirect(r'../filebaseinfoadd/'+str(dynamicsubjectid))
            else:
                messages.info(req, '请选择该专题下确定子专题！')
                return redirect(r'..', {})

            # 测试界面
            # return redirect(r'../subjectinfoadd', {'abc': form})
    else:
        form = ChoiceForm()
        global level
        level = 1
        data = getsubject(None,1)
        global levelist
        levelist = []
        for i in range(0, level):
            levelist.append('level_' + str(i))
        return render_to_response('xadmin/himalaya/filebaseinfo/add.html', {'username':req.user,'level':levelist,'data':json.dumps(data)})


# 获得FileType所有的类型
def get_filetypechoices():
    ftsf = []
    ftsfid = []
    for i in range(0, len(FileType.objects.all())):
        ftsf.append(FileType.objects.all()[i].fileTypeName)
        ftsfid.append(FileType.objects.all()[i].id)
    ft_choice = zip(ftsfid, ftsf)
    return ft_choice


# 获得Language所有的类型
def get_languagechoices():
    ftsf = []
    ftsfid = []
    for i in range(0, len(Language.objects.all())):
        ftsf.append(Language.objects.all()[i].lanTypeName)
        ftsfid.append(Language.objects.all()[i].id)
    ft_choice = zip(ftsfid, ftsf)
    return ft_choice


# 获得SpaceScope所有的类型
def get_spacescopechoices():
    ftsf = []
    ftsfid = []
    for i in range(0, len(SpaceScope.objects.all())):
        ftsf.append(SpaceScope.objects.all()[i].spcaeTypeName)
        ftsfid.append(SpaceScope.objects.all()[i].id)
    ft_choice = zip(ftsfid, ftsf)
    return ft_choice


# 获得Discipline所有的类型
def get_disciplinechoices():
    ftsf = []
    ftsfid = []
    for i in range(0, len(Discipline.objects.all())):
        ftsf.append(Discipline.objects.all()[i].disciplineTypeName)
        ftsfid.append(Discipline.objects.all()[i].id)
    ft_choice = zip(ftsfid, ftsf)
    return ft_choice


# 获得Format所有的类型
def get_formatchoices():
    ftsf = []
    ftsfid = []
    for i in range(0, len(Format.objects.all())):
        ftsf.append(Format.objects.all()[i].formatTypeName)
        ftsfid.append(Format.objects.all()[i].id)
    ft_choice = zip(ftsfid, ftsf)
    return ft_choice




def filebaseinfoadd(req,dynamicsubjectid):
    if req.method == 'POST':
            form = FileBaseInfoForm(req.POST, req.FILES)
            fbi = FileBaseInfo()
            fbi.filecode = form['filecode'].value()
            req.session['filecode'] = form['filecode'].value()
            fbi.title = form['title'].value()
            req.session['title'] = form['title'].value()
            fbi.creator = form['creator'].value()
            req.session['creator'] = form['creator'].value()

            strrrr = str(form['keywords'].value()).replace(' ', '').replace('；', ';')

            fbi.keywords = strrrr
            req.session['keywords'] = strrrr
            fbi.description = form['description'].value()
            req.session['description'] = form['description'].value()
            fbi.publisher = form['publisher'].value()
            req.session['publisher'] = form['publisher'].value()
            fileType = form['fileType'].value()
            req.session['fileType'] = form['fileType'].value()
            language = form['language'].value()
            req.session['language'] = form['language'].value()
            discipline = form['discipline'].value()
            req.session['discipline'] = form['discipline'].value()

            spatial = form['spatial'].value()
            req.session['spatial'] = form['spatial'].value()
            fileFormat = form['fileFormat'].value()
            req.session['fileFormat'] = form['fileFormat'].value()
            fbi.contributor = form['contributor'].value()
            req.session['contributor'] = form['contributor'].value()

            # print form['pubDate'].value()
            # l = str(form['pubDate'].value()).split('/')
            # fbi.pubDate = datetime.strptime(''.join(l), "%Y%m%d").date()
            # l = (str(form['pubdate'].value())+'/01/01').split('/')
            # fbi.pubDate = datetime.strptime(''.join(l), "%Y%m%d").date()
            req.session['pubdate'] = ''
            if(len(form['pubdate'].value())!=0 and str(form['pubdate'].value()) !='0'):
                strcreatedate = ''
                if (int(form['pubdate'].value()) >= 10000):

                    strcreatedate = str(form['pubdate'].value())[0:4]
                elif (len(str(form['pubdate'].value())) == 1):
                    strcreatedate = '000' + str(form['pubdate'].value())
                elif (len(str(form['pubdate'].value())) == 2):
                    strcreatedate = '00' + str(form['pubdate'].value())
                elif (len(str(form['pubdate'].value())) == 3):
                    strcreatedate = '0' + str(form['pubdate'].value())
                else:
                    strcreatedate = str(form['pubdate'].value())
                createdate = ((strcreatedate) + '/01/01').split('/')
                req.session['pubdate'] =strcreatedate
                fbi.pubDate = datetime.strptime(''.join(createdate), "%Y%m%d").date()

            fbi.contentLength = form['contentLength'].value()
            req.session['contentLength'] = form['contentLength'].value()
            fbi.uploadPeople = form['uploadPeople'].value()
            req.session['uploadPeople'] = form['uploadPeople'].value()

            # print 'fffffffff',time.localtime(time.time())
            # fbi.uploadDate = time.localtime(time.time())
            # fbi.updateDate = time.strftime('%Y-%m-%d', time.localtime(time.time()))

            # // 把上传的文件下载到本地里。
            if(int(dynamicsubjectid)==0):
                fbi.picture = form['picture'].value()
                # headImg=form.cleaned_data['picture'].name
                # headImg= str(time.time())+headImg
                # print 'rrrrrrrrrrr',headImg
                #
                # fp = file('./media/himalaya/images/' + headImg, 'wb')
                # s = form.cleaned_data['picture'].read()
                # fp.write(s)
                # fp.close()
                # req.session['picture'] ='himalaya/images/'+ headImg



            # req.session['picture'] = form['picture'].value()

                fbi.attachment = form['attachment'].value()
                # # req.session['attachment'] = form['attachment'].value()
                # attachment = form.cleaned_data['attachment'].name
                # attachment = str(time.time()) + attachment
                # print 'ttttttttttt', attachment
                #
                # fp = file('./media/himalaya/files/' + attachment, 'wb')
                # s = form.cleaned_data['attachment'].read()
                # fp.write(s)
                # fp.close()
                # req.session['attachment'] ='himalaya/files/'+ attachment
                fbi.size = fbi.attachment.size
                # req.session['size'] = fbi.attachment.size


            fbi.notes = form['notes'].value()
            req.session['notes'] = form['notes'].value()




            # 如果dynamicsubjectid存储。
            if(int(dynamicsubjectid)==0):
                fbi.subjecttype=-1

                newfbi=FileBaseInfo.objects.all().filter(title__exact=fbi.title).filter(filecode__exact=fbi.filecode).filter(creator__exact
                                                =fbi.creator).filter(keywords__exact=fbi.keywords).filter(description__exact=fbi.description).filter(publisher__exact
                                                =fbi.publisher).filter(contributor__exact=fbi.contributor).filter(subjecttype=-1)
                print 'cccccccccccccccccc',len(newfbi)
                if(len(newfbi)==0):
                    fbi.save()
                    fbii = FileBaseInfo.objects.all()[len(FileBaseInfo.objects.all()) - 1]
                # 记录产生的基础文献的id

                    dynamicfilebaseid = fbii.id
                    # 添加多对多表，用add
                    id_list = [int(x) for x in fileType]
                    for i in id_list:
                        fbii.fileType.add(i)

                    id_list = [int(x) for x in language]
                    for i in id_list:
                        fbii.language.add(i)

                    id_list = [int(x) for x in discipline]
                    for i in id_list:
                        fbii.discipline.add(i)

                    id_list = [int(x) for x in spatial]

                    for i in id_list:
                        fbii.spatial.add(i)

                    id_list = [int(x) for x in fileFormat]

                    for i in id_list:
                        fbii.fileFormat.add(i)

                else:
                    print 'eeeeeeeeeee',newfbi[0].id
                    fbii =FileBaseInfo.objects.all().get(id=newfbi[0].id)
                    id_list = [int(x) for x in fileType]
                    for i in id_list:
                        fbii.fileType.add(i)
                    id_list = [int(x) for x in language]
                    for i in id_list:
                        fbii.language.add(i)

                    id_list = [int(x) for x in discipline]
                    for i in id_list:
                        fbii.discipline.add(i)

                    id_list = [int(x) for x in spatial]

                    for i in id_list:
                        fbii.spatial.add(i)

                    id_list = [int(x) for x in fileFormat]

                    for i in id_list:
                        fbii.fileFormat.add(i)

            else:
                fbi.subjecttype =int(dynamicsubjectid)

            if (int(dynamicsubjectid) == 0):
                # 跳转到文献基础库列表页面
                messages.info(req, '基础文献保存成功')
                return redirect(r'../..', {})
            else:
                return redirect(r'../../subjectinfoadd/'+str(dynamicsubjectid), {})


    else:
        form = FileBaseInfoForm()


    return render_to_response('xadmin/himalaya/filebaseinfo/filebaseinfoadd.html',
                              {'form': form, 'ftchoice': get_filetypechoices(),
                               'sschoice': get_spacescopechoices(), 'lanchoice': get_languagechoices(),
                               'dischoice': get_disciplinechoices(),
                               'forchoice': get_formatchoices(), 'sujectidd': int(dynamicsubjectid),'username':req.user})





# 遍历树
def fill_topic_tree(deep=0, parent_id=0, choicess=[]):

    ts = Category.objects.filter(pid_id=parent_id)
    for t in ts:
        choicess[0] += ((t.id, '-' * deep + t.attrName, deep / 4),)
        fill_topic_tree(deep + 4, t.id, choicess)


def tree_choices(parentid):
    choicess = [()]
    fill_topic_tree(parent_id=parentid, choicess=choicess)

    # 把choicess最外层的【（）】小括号去掉
    # 按逗号分开
    strchoice = choicess
    if (len(strchoice[0]) == 0):
        return zip([], [])
    else:
        tur = strchoice[0]
        trid = []
        trchoice = []
        for i in range(0, len(tur)):
            trid.append(tur[i][0])
            trchoice.append(tur[i][1])
        tr_choices = zip(trid, trchoice)
    return tr_choices



def kongtree_choices(parentid):
    choicess = [()]
    fill_topic_tree(parent_id=parentid, choicess=choicess)

    # 把choicess最外层的【（）】小括号去掉
    # 按逗号分开
    strchoice = choicess
    if (len(strchoice[0]) == 0):
        return zip([], [])
    else:
        tur = strchoice[0]
        trid = [-1]
        trchoice = ['']
        for i in range(0, len(tur)):
            trid.append(tur[i][0])
            trchoice.append(tur[i][1])
        tr_choices = zip(trid, trchoice)
    return tr_choices



def sujectinfoadd(req, dynamicfilebaseid):
    # 定义一个变量判断扩展属性页面显示的样式，是否有扩展属性。
    global addkuozhanshuxing
    addkuozhanshuxing = True
    global flag
    global datatree
    global levelist
    # 动态生成表单
    class SujectThemeDynamicForm(forms.Form):
        dynamicsubjectid = int(dynamicfilebaseid)
        if (dynamicsubjectid == -1):
            pass
        else:
            # sstr,iint,ffloat,ddate,eenum,ttree,bboolean代表数据库sujectid=选择专题id，且类型为对应的数据
            #创建图片和文档
            picture=forms.ImageField(label='picture',required=False)
            attachment=forms.FileField(label='attachment',required=False)
            # picture = models.ImageField(upload_to='himalaya/images', verbose_name='picture', blank=True)
            # attachment = models.FileField(upload_to='himalaya/files', verbose_name='attachment', blank=True)
            global sstr, iint, ffloat, ddate, bboolean, eenum, ttree
            sstr = SubjectTheme.objects.filter(subjectId=dynamicsubjectid).filter(fieldType='0')
            iint = SubjectTheme.objects.filter(subjectId=dynamicsubjectid).filter(fieldType='1')
            ffloat = SubjectTheme.objects.filter(subjectId=dynamicsubjectid).filter(fieldType='2')
            ddate = SubjectTheme.objects.filter(subjectId=dynamicsubjectid).filter(fieldType='3')
            bboolean = SubjectTheme.objects.filter(subjectId=dynamicsubjectid).filter(fieldType='4')
            eenum = SubjectTheme.objects.filter(subjectId=dynamicsubjectid).filter(fieldType='5')
            ttree = SubjectTheme.objects.filter(subjectId=dynamicsubjectid).filter(fieldType='6')
            # num代表数据库里的数据条数
            global sstrnum, iintnum, ffloatnum, ddatenum, bbooleannum, eenumnum, ttreenum
            sstrnum = len(sstr)
            iintnum = len(iint)
            ffloatnum = len(ffloat)
            ddatenum = len(ddate)
            bbooleannum = len(bboolean)
            eenumnum = len(eenum)
            ttreenum = len(ttree)

            if ((sstrnum == 0) and (iintnum == 0) and (ffloatnum == 0) and (ddatenum == 0)
                and (bbooleannum == 0) and (eenumnum == 0) and (ttreenum == 0)):
                global addkuozhanshuxing
                addkuozhanshuxing=False
            # sstrnames动态创建表单的名字，并且创建对应的属性字段
            sstrnames = locals()
            for i in xrange(0, sstrnum):
                if (sstr[i].isMust):
                    sstrnames['sstr%s' % i] = forms.CharField(label=sstr[i].fieldName + '*',
                                                              help_text=sstr[i].promtInfo,required=False)
                else:
                    sstrnames['sstr%s' % i] = forms.CharField(label=sstr[i].fieldName,
                                                              help_text=sstr[i].promtInfo,required=False)

            iintnames = locals()
            for i in xrange(0, iintnum):
                if (iint[i].isMust):
                    iintnames['iint%s' % i] = forms.IntegerField(label=iint[i].fieldName + '*',
                                                                 help_text=iint[i].promtInfo,required=False)
                else:
                    iintnames['iint%s' % i] = forms.IntegerField(label=iint[i].fieldName,
                                                                 help_text=iint[i].promtInfo,required=False)

            ffloatnames = locals()
            for i in xrange(0, ffloatnum):
                if (ffloat[i].isMust):
                    ffloatnames['ffloat%s' % i] = forms.FloatField(
                                                                   label=ffloat[i].fieldName + '*',
                                                                   help_text=ffloat[i].promtInfo,required=False)
                else:
                    ffloatnames['ffloat%s' % i] = forms.FloatField( label=ffloat[i].fieldName,
                                                                   help_text=ffloat[i].promtInfo,required=False)

            ddatenames = locals()
            for i in xrange(0, ddatenum):
                if (ddate[i].isMust):
                    ddatenames['ddate%s' % i] = forms.DateField(
                                                                label=ddate[i].fieldName + '*',
                                                                help_text=ddate[i].promtInfo,required=False)
                else:
                    ddatenames['ddate%s' % i] = forms.DateField(
                                                                label=ddate[i].fieldName, help_text=ddate[i].promtInfo,required=False)

            bbooleannames = locals()
            for i in xrange(0, bbooleannum):
                if (bboolean[i].isMust):
                    bbooleannames['bboolean%s' % i] = forms.TypedChoiceField(
                                                                             coerce=lambda x: x == 'True',
                                                                             choices=((False, 'False'), (True, 'True')),
                                                                             widget=forms.RadioSelect,
                                                                             label=bboolean[i].fieldName + '*',
                                                                             help_text=bboolean[i].promtInfo,
                                                                             initial=False,required=False)
                else:
                    bbooleannames['bboolean%s' % i] = forms.TypedChoiceField(
                                                                             coerce=lambda x: x == 'True',
                                                                             choices=((False, 'False'), (True, 'True')),
                                                                             widget=forms.RadioSelect,
                                                                             label=bboolean[i].fieldName + '*',
                                                                             help_text=bboolean[i].promtInfo,
                                                                             initial=False,required=False)

            # 枚举类型的定义
            eenumnames = locals()
            for i in xrange(0, eenumnum):
                choicess = [()]
                fill_topic_tree(parent_id=eenum[i].corrAttri, choicess=choicess)
                if (len(choicess[0]) != 0):
                    if (eenum[i].isMust):
                        eenumnames['eenum%s' % i] = forms.MultipleChoiceField(
                                                                      label=eenum[i].fieldName + '*',
                                                                      help_text='多选按Ctril键',
                                                                      choices=tree_choices(eenum[i].corrAttri),required=False)
                    else:
                        eenumnames['eenum%s' % i] = forms.MultipleChoiceField(
                                                                      label=eenum[i].fieldName,
                                                                      help_text='多选按Ctril键',
                                                                      choices=kongtree_choices(eenum[i].corrAttri),required=False)

            # 树类型定义
            ttreenames = locals()
            global creatree
            creatree = []
            crealevel = []
            ttreenames = locals()

            for i in xrange(0, ttreenum):
                sd = Category.objects.get(id=ttree[i].corrAttri)
                # while (sd.pid_id != 0):
                #     sd = sd.pid
                if (int(sd.id) == 273):
                    target = Category.objects.get(id=int(ttree[i].corrAttri))
                    with open('creatree.pkl', 'rb') as file:
                        ass = cPickle.load(file)
                        file.close()
                    data = ass[0]
                    level = ass[1]
                    global levelist
                    levelist = []
                    for j in range(0, len(level)):
                        levelist.append(str('0') + '_level_' + str(j))
                    global creatree
                    if (ttree[i].isMust):
                        creatree.append(
                            [ttree[i].fieldName, [levelist, json.dumps(data)], ttree[i].id, 1, ttree[i].promtInfo])
                    else:
                        creatree.append(
                            [ttree[i].fieldName, [levelist, json.dumps(data)], ttree[i].id, 0, ttree[i].promtInfo])
                else:
                    choicess = [()]
                    fill_topic_tree(parent_id=ttree[i].corrAttri, choicess=choicess)
                    if (len(choicess[0]) != 0):
                        if (ttree[i].isMust):
                            ttreenames['ttree%s' % i] = forms.MultipleChoiceField(
                                                                          label=ttree[i].fieldName + '*',
                                                                          help_text='多选按Ctril键',
                                                                          choices=tree_choices(ttree[i].corrAttri),required=False)
                        else:
                            ttreenames['ttree%s' % i] = forms.MultipleChoiceField(
                                                                          label=ttree[i].fieldName,
                                                                          help_text='多选按Ctril键',
                                                                          choices=kongtree_choices(ttree[i].corrAttri),required=False)





                        # 添加时候已经有了处理

    if req.method == 'POST':
        form = SujectThemeDynamicForm(req.POST,req.FILES)
        if form.is_valid():
            newfbs=FileBaseInfo.objects.all().filter(title__exact=req.session.get('title',default=None)).filter(filecode__exact=req.session.get('filecode',default=None)).filter(creator__exact
                                                =req.session.get('creator',default=None)).filter(keywords__exact=req.session.get('keywords',default=None)).filter(description__exact=req.session.get('description',default=None)).filter(publisher__exact=req.session.get('publisher',default=None)).filter(subjecttype=int(dynamicfilebaseid))
            if(len(newfbs)==0):
                fbi = FileBaseInfo()
                fbi.filecode = req.session.get('filecode',default=None)
                fbi.title = req.session.get('title',default=None)
                fbi.creator = req.session.get('creator',default=None)
                fbi.keywords = req.session.get('keywords',default=None)
                fbi.description = req.session.get('description',default=None)
                fbi.publisher = req.session.get('publisher',default=None)
                fbi.contributor =  req.session.get('contributor',default=None)
                if req.session.get('pubdate',default=None) !='':
                    createdate = ((req.session.get('pubdate',default=None)) + '/01/01').split('/')
                    fbi.pubDate = datetime.strptime(''.join(createdate), "%Y%m%d").date()
                fbi.contentLength = req.session.get('contentLength',default=None)
                fbi.uploadPeople = req.session.get('uploadPeople',default=None)
                # // 把上传的文件下载到本地里。


                # fbi.picture = form['picture'].value()
                headImg=form.cleaned_data['picture'].name
                headImg= str(time.time())+headImg
                fp = file('./media/himalaya/images/' + headImg, 'wb')
                s = form.cleaned_data['picture'].read()
                fp.write(s)
                fp.close()
                fbi.picture.name = 'himalaya/images/'+ headImg
                attachment = form.cleaned_data['attachment'].name
                attachment = str(time.time()) + attachment


                fp = file('./media/himalaya/files/' + attachment, 'wb')
                s = form.cleaned_data['attachment'].read()
                fp.write(s)
                fp.close()
                fbi.attachment.name = 'himalaya/files/'+ attachment
                fbi.size = form.cleaned_data['attachment'].size


                # fbi.size = req.session.get('size', default=None)

                fbi.notes = req.session.get('notes',default=None)

                fbi.subjecttype =dynamicfilebaseid
                fbi.save()
                fbii = FileBaseInfo.objects.all()[len(FileBaseInfo.objects.all()) - 1]
                        # 记录产生的基础文献的id
                dynamicfilebaseid = fbi.id
                print '2222222222222',dynamicfilebaseid

                        # 添加多对多表，用add
                id_list = [int(x) for x in req.session.get('fileType',default=None)]
                for i in id_list:
                    fbii.fileType.add(i)

                id_list = [int(x) for x in req.session.get('language',default=None)]
                for i in id_list:
                    fbii.language.add(i)

                id_list = [int(x) for x in req.session.get('discipline',default=None)]
                for i in id_list:
                    fbii.discipline.add(i)

                id_list = [int(x) for x in req.session.get('spatial',default=None)]

                for i in id_list:
                    fbii.spatial.add(i)

                id_list = [int(x) for x in req.session.get('fileFormat',default=None)]

                for i in id_list:
                    fbii.fileFormat.add(i)
            else:
                dynamicfilebaseid = newfbs[0].id
                print '33333333333333',dynamicfilebaseid
                fbii=newfbs[0]
                # 添加多对多表，用add
                id_list = [int(x) for x in req.session.get('fileType', default=None)]
                for i in id_list:
                    fbii.fileType.add(i)

                id_list = [int(x) for x in req.session.get('language', default=None)]
                for i in id_list:
                    fbii.language.add(i)

                id_list = [int(x) for x in req.session.get('discipline', default=None)]
                for i in id_list:
                    fbii.discipline.add(i)

                id_list = [int(x) for x in req.session.get('spatial', default=None)]

                for i in id_list:
                    fbii.spatial.add(i)

                id_list = [int(x) for x in req.session.get('fileFormat', default=None)]

                for i in id_list:
                    fbii.fileFormat.add(i)

            global sstr, iint, ffloat, ddate, bboolean, eenum, ttree
            global sstrnum, iintnum, ffloatnum, ddatenum, bbooleannum, eenumnum, ttreenum
            filebaseid = int(dynamicfilebaseid)
            for i in range(0, sstrnum):
                if (len(FileExtendInfo.objects.filter(fileId=filebaseid).filter(fieldId=sstr[i].id)) == 0):
                    fileextend = FileExtendInfo()
                    fileextend.fileId = int(filebaseid)
                    fileextend.fieldId = int(sstr[i].id)
                    fileextend.filedValue = form['sstr%s' % i].value()
                    fileextend.save()
                else:
                    fileextendupdate = FileExtendInfo.objects.filter(fileId=filebaseid).get(fieldId=sstr[i].id)
                    fileextendupdate.filedValue = form['sstr%s' % i].value()
                    fileextendupdate.save()
            for i in range(0, iintnum):
                if (len(FileExtendInfo.objects.filter(fileId=filebaseid).filter(fieldId=iint[i].id)) == 0):
                    fileextend = FileExtendInfo()
                    fileextend.fileId = int(filebaseid)
                    fileextend.fieldId = int(iint[i].id)
                    fileextend.filedValue = form['iint%s' % i].value()
                    fileextend.save()
                else:
                    fileextendupdate = FileExtendInfo.objects.filter(fileId=filebaseid).get(fieldId=iint[i].id)
                    fileextendupdate.filedValue = form['iint%s' % i].value()
                    fileextendupdate.save()
            for i in range(0, ffloatnum):
                if (len(FileExtendInfo.objects.filter(fileId=filebaseid).filter(fieldId=ffloat[i].id)) == 0):
                    fileextend = FileExtendInfo()
                    fileextend.fileId = int(filebaseid)
                    fileextend.fieldId = int(ffloat[i].id)
                    fileextend.filedValue = form['ffloat%s' % i].value()
                    fileextend.save()
                else:
                    fileextendupdate = FileExtendInfo.objects.filter(fileId=filebaseid).get(fieldId=ffloat[i].id)
                    fileextendupdate.filedValue = form['ffloat%s' % i].value()
                    fileextendupdate.save()
            for i in range(0, ddatenum):
                if (len(FileExtendInfo.objects.filter(fileId=filebaseid).filter(fieldId=ddate[i].id)) == 0):
                    fileextendupdate = FileExtendInfo()
                    fileextendupdate.fileId = int(filebaseid)
                    fileextendupdate.fieldId = ddate[i].id
                    if (len(form['ddate%s' % i].value()) != 0):
                        createdate = str(form['ddate%s' % i].value()).split('/')
                        if (len(createdate) == 3):
                            fileextendupdate.filedValue = datetime.strptime(''.join(createdate),
                                                                            "%Y%m%d").date()
                            fileextendupdate.save()
                    else:
                        fileextendupdate.filedValue = form['ddate%s' % i].value()
                        fileextendupdate.save()
                else:
                    fileextendupdate = FileExtendInfo.objects.filter(fileId=filebaseid).get(fieldId=ddate[i].id)
                    if (len(form['ddate%s' % i].value()) != 0):
                        createdate = str(form['ddate%s' % i].value()).split('/')
                        if (len(createdate) == 3):
                            fileextendupdate.filedValue = datetime.strptime(''.join(createdate),
                                                                            "%Y%m%d").date()
                            fileextendupdate.save()
                    else:
                        fileextendupdate.filedValue = form['ddate%s' % i].value()
                        fileextendupdate.save()
            for i in range(0, bbooleannum):
                if (len(FileExtendInfo.objects.filter(fileId=filebaseid).filter(fieldId=bboolean[i].id)) == 0):
                    fileextendupdate = FileExtendInfo()
                    fileextendupdate.fileId = filebaseid
                    fileextendupdate.fieldId = bboolean[i].id
                    fileextendupdate.filedValue = form['bboolean%s' % i].value()
                    fileextendupdate.save()
                else:
                    fileextendupdate = FileExtendInfo.objects.filter(fileId=filebaseid).get(fieldId=bboolean[i].id)
                    fileextendupdate.filedValue = form['bboolean%s' % i].value()
                    fileextendupdate.save()
            # for i in range(0, eenumnum):
            #     choicess = [()]
            #     choicess = [()]
            #     fill_topic_tree(parent_id=eenum[i].corrAttri, choicess=choicess)
            #     if ((len(choicess[0]) != 0) and (len(form['eenum%s' % i].value()) != 0)):
            #         for item in form['eenum%s' % i].value():
            #             if (len(FileExtendInfo.objects.filter(fileId=filebaseid).filter(fieldId=eenum[i].id)) == 0):
            #                 fileextendupdate = FileExtendInfo()
            #                 fileextendupdate.fileId = filebaseid
            #                 fileextendupdate.fieldId = eenum[i].id
            #                 fileextendupdate.filedValue = item
            #                 fileextendupdate.save()
            #             else:
            #                 fileextendupdate = FileExtendInfo.objects.filter(fileId=filebaseid).get(fieldId=eenum[i].id)
            #                 fileextendupdate.filedValue = item
            #                 fileextendupdate.save()
            for i in range(0, ttreenum):
                sd = Category.objects.get(id=ttree[i].corrAttri)
                # while (sd.pid_id != 0):
                #     sd = sd.pid
                if (int(sd.id) == 273):
                    continue
                else:
                    choicess = [()]
                    fill_topic_tree(parent_id=ttree[i].corrAttri, choicess=choicess)
                    if ((len(choicess[0]) != 0) and len(form['ttree%s' % i].value()) != 0):
                        print(form['ttree%s' % i].value())
                        for item in form['ttree%s' % i].value():
                            if (len(FileExtendInfo.objects.filter(fileId=filebaseid).filter(fieldId=ttree[i].id)) == 0):
                                fileextendupdate = FileExtendInfo()
                                fileextendupdate.fileId = filebaseid
                                fileextendupdate.fieldId = ttree[i].id
                                fileextendupdate.filedValue = item
                                fileextendupdate.save()
                            else:
                                fileextendupdate = FileExtendInfo.objects.filter(fileId=filebaseid).get(fieldId=ttree[i].id)
                                fileextendupdate.filedValue = item
                                fileextendupdate.save()
            global creatree
            for treei in range(0,len(creatree)):
            #     循环每颗树的层次
                for treej in range(len(creatree[treei][1][0])-1,-1,-1):
                    fieldId=creatree[treei][2]
                    filedvalue=req.POST.get(str(treei)+'_level_'+str(treej))
                    if(filedvalue):
                        print 'id:',dynamicfilebaseid,'fieldId:',creatree[treei][2],'filedValue:',filedvalue,'1111'
                        if (len(FileExtendInfo.objects.filter(fileId=filebaseid).filter(fieldId=fieldId)) == 0):
                            fileextendupdate = FileExtendInfo()
                            fileextendupdate.fileId = filebaseid
                            fileextendupdate.fieldId = fieldId
                            fileextendupdate.filedValue = filedvalue
                            fileextendupdate.save()
                        else:
                            fileextendupdate = FileExtendInfo.objects.filter(fileId=filebaseid).get(fieldId=fieldId)
                            fileextendupdate.filedValue = filedvalue
                            fileextendupdate.save()
                        break

            # 添加成功跳转
            messages.info(req, '专题文献成功')
            return redirect(r'../..', {})
    else:
        form = SujectThemeDynamicForm()
    global addkuozhanshuxing
    print 'ccccccccccccccccckuozhanshuxing',addkuozhanshuxing
    print 'dddddddddd',req.session.get('picture',default=None)
    global creatree
    return render_to_response('xadmin/himalaya/filebaseinfo/subjectinfoadd.html',
                              {'form': form, 'data':creatree,'categories': Category.objects.filter(pid_id=None),'kuozhanshuxing':addkuozhanshuxing,'username':req.user})



# 文献的编辑
def filebaseinfoedit(req, id):
    if req.method == 'POST':
        formupdate = FileBaseInfo.objects.get(id=int(id))
        formnew = FileBaseInfoForm(req.POST, req.FILES)
        formupdate.filecode = formnew['filecode'].value()
        formupdate.title = formnew['title'].value()
        formupdate.creator = formnew['creator'].value()
        strrrr=str(formnew['keywords'].value()).replace(' ','').replace('；',';')
        formupdate.keywords = strrrr
        formupdate.description = formnew['description'].value()
        formupdate.publisher = formnew['publisher'].value()
        formupdate.fileType = formnew['fileType'].value()
        formupdate.language = formnew['language'].value()
        formupdate.discipline = formnew['discipline'].value()
        formupdate.spatial = formnew['spatial'].value()
        formupdate.fileFormat = formnew['fileFormat'].value()
        formupdate.contributor = formnew['contributor'].value()
        if (len(formnew['pubdate'].value() )!=0  and str(formnew['pubdate'].value()) !='0'):
            strcreatedate = ''
            if (int(formnew['pubdate'].value()) >= 10000):
                strcreatedate = str(formnew['pubdate'].value())[0:4]
            elif(len(str(formnew['pubdate'].value()))==1):
                strcreatedate='000'+str(formnew['pubdate'].value())
            elif (len(str(formnew['pubdate'].value())) == 2):
                strcreatedate = '00' + str(formnew['pubdate'].value())
            elif (len(str(formnew['pubdate'].value())) == 3):
                strcreatedate = '0' + str(formnew['pubdate'].value())
            else:
                strcreatedate = str(formnew['pubdate'].value())
            print 'ccccccccc', strcreatedate
            createdate = ((strcreatedate) + '/01/01').split('/')
            formupdate.pubDate = datetime.strptime(''.join(createdate), "%Y%m%d").date()
        else:
            form = FileBaseInfo.objects.get(id=int(id))
            if(len(str(form.pubDate))!=0):
                formupdate.pubDate=None
        # formupdate.pubDate=formnew['pubDate'].value()
        if formnew['contentLength'].value()!='':
            formupdate.contentLength = formnew['contentLength'].value()
        # formupdate.contentLength = formnew['contentLength'].value()
        formupdate.uploadPeople = formnew['uploadPeople'].value()
        # formupdate.updateDate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        if (len(str(formnew['picture'].value()).split('.')) == 2):
            s = formupdate.picture
            s = './media/' + str(s)
            s = s.decode('utf-8')
            if os.path.exists(s) and os.path.isfile(s):
                os.remove(s)
            formupdate.picture = formnew['picture'].value()
        if (len(str(formnew['attachment'].value()).split('.')) == 2):
            s1 = formupdate.attachment
            s = './media/' + str(s1)
            s = s.decode('utf-8')
            if os.path.exists(s) and os.path.isfile(s):
                os.remove(s)
            formupdate.attachment = formnew['attachment'].value()
            formupdate.size = formupdate.attachment.size
        formupdate.notes = formnew['notes'].value()
        formupdate.save()

        if (formupdate.subjecttype == -1):
            messages.info(req, '修改成功')
            return redirect('../..', {})
        else:
            return redirect(r'../../../fileextendinfo/' + str(id) + '/update', {})
        formnew = ViewForm(req.POST, req.FILES)

    try:
        form = FileBaseInfo.objects.get(id=int(id))
        fileherf = r'/media/' + form.attachment.name.encode("UTF-8")
        picherf = r'/media/' + form.picture.name.encode("UTF-8")
    except View.DoesNotExist:
        return render_to_response('xadmin/404.html', {})
    return render_to_response('xadmin/himalaya/filebaseinfo/update.html',
                              {'form': form, 'ftchoice': get_filetypechoices(),
                               'sschoice': get_spacescopechoices(), 'lanchoice': get_languagechoices(),
                               'dischoice': get_disciplinechoices(),
                               'forchoice': get_formatchoices(), 'fileherf': fileherf, 'picherf': picherf,
                               'sujectidd': form.subjecttype,'username':req.user})


# 扩展属性编辑
# 扩展属性编辑
def fileextendinfoedit(req, id):
    # 动态生成表单
    print 'cccccccccccccccc'
    sujectidd = FileBaseInfo.objects.get(id=int(id)).subjecttype
    global editkuozhanshuxing
    editkuozhanshuxing=True
    class SujectThemeDynamicForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super(SujectThemeDynamicForm, self).__init__(*args, **kwargs)
            print 'mmmmmmmmmmm',self.initvalue
            self.initial['ttree5'] = str('49109')
            # sstr,iint,ffloat,ddate,eenum,ttree,bboolean代表数据库sujectid=选择专题id，且类型为对应的数据
        global sstr, iint, ffloat, ddate, bboolean, eenum, ttree
        sstr = SubjectTheme.objects.filter(subjectId=sujectidd).filter(fieldType='0')
        iint = SubjectTheme.objects.filter(subjectId=sujectidd).filter(fieldType='1')
        ffloat = SubjectTheme.objects.filter(subjectId=sujectidd).filter(fieldType='2')
        ddate = SubjectTheme.objects.filter(subjectId=sujectidd).filter(fieldType='3')
        bboolean = SubjectTheme.objects.filter(subjectId=sujectidd).filter(fieldType='4')
        eenum = SubjectTheme.objects.filter(subjectId=sujectidd).filter(fieldType='5')
        ttree = SubjectTheme.objects.filter(subjectId=sujectidd).filter(fieldType='6')
        # num代表数据库里的数据条数
        global sstrnum, iintnum, ffloatnum, ddatenum, bbooleannum, eenumnum, ttreenum
        sstrnum = len(sstr)
        iintnum = len(iint)
        ffloatnum = len(ffloat)
        ddatenum = len(ddate)
        bbooleannum = len(bboolean)
        eenumnum = len(eenum)
        ttreenum = len(ttree)

        if ((sstrnum == 0) and (iintnum == 0) and (ffloatnum == 0) and (ddatenum == 0)
            and (bbooleannum == 0) and (eenumnum == 0) and (ttreenum == 0)):
            global editkuozhanshuxing
            editkuozhanshuxing = False
        print 'bbbbbbbbbbbbbbbbbbbbbkuozhanshuxing', editkuozhanshuxing

        # sstrnames动态创建表单的名字，并且创建对应的属性字段
        sstrnames = locals()
        for i in xrange(0, sstrnum):
            initvalue = ''
            if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=sstr[i].id)) != 0):
                initvalue = FileExtendInfo.objects.filter(fileId=id).get(fieldId=sstr[i].id).filedValue

            if (sstr[i].isMust):
                sstrnames['sstr%s' % i] = forms.CharField(label=sstr[i].fieldName + '*',
                                                          help_text=sstr[i].promtInfo, initial=initvalue,
                                                          error_messages={'required': '必须填写'})
            else:
                sstrnames['sstr%s' % i] = forms.CharField(label=sstr[i].fieldName,
                                                          help_text=sstr[i].promtInfo, initial=initvalue)

        iintnames = locals()
        for i in xrange(0, iintnum):
            initvalue = ''
            if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=iint[i].id)) != 0):
                initvalue = FileExtendInfo.objects.filter(fileId=id).get(fieldId=iint[i].id).filedValue
            if (iint[i].isMust):
                iintnames['iint%s' % i] = forms.IntegerField(label=iint[i].fieldName + '*',
                                                             help_text=iint[i].promtInfo, initial=initvalue)
            else:
                iintnames['iint%s' % i] = forms.IntegerField(label=iint[i].fieldName,
                                                             help_text=iint[i].promtInfo, initial=initvalue)

        ffloatnames = locals()
        for i in xrange(0, ffloatnum):
            initvalue = ''
            if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=ffloat[i].id)) != 0):
                initvalue = FileExtendInfo.objects.filter(fileId=id).get(fieldId=ffloat[i].id).filedValue
            if (ffloat[i].isMust):
                ffloatnames['ffloat%s' % i] = forms.FloatField(
                                                               label=ffloat[i].fieldName + '*',
                                                               help_text=ffloat[i].promtInfo, initial=initvalue)
            else:
                ffloatnames['ffloat%s' % i] = forms.FloatField(label=ffloat[i].fieldName,
                                                               help_text=ffloat[i].promtInfo, initial=initvalue)

        ddatenames = locals()
        for i in xrange(0, ddatenum):
            initvalue = ''
            if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=ddate[i].id)) != 0):
                initvalue = FileExtendInfo.objects.filter(fileId=id).get(fieldId=ddate[i].id).filedValue
            if (ddate[i].isMust):
                ddatenames['ddate%s' % i] = forms.DateField(required=ddate[i].isMust,
                                                            label=ddate[i].fieldName + '*',
                                                            help_text=ddate[i].promtInfo, initial=initvalue)
            else:
                ddatenames['ddate%s' % i] = forms.DateField(required=ddate[i].isMust,
                                                            label=ddate[i].fieldName, help_text=ddate[i].promtInfo,
                                                            initial=initvalue)

        bbooleannames = locals()
        for i in xrange(0, bbooleannum):
            initvalue = False
            if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=bboolean[i].id)) != 0):
                initvalue = FileExtendInfo.objects.filter(fileId=id).get(fieldId=bboolean[i].id).filedValue

            if (bboolean[i].isMust):
                bbooleannames['bboolean%s' % i] = forms.TypedChoiceField(required=False, coerce=lambda x: x == 'True',
                                                                         choices=((False, 'False'), (True, 'True')),
                                                                         widget=forms.RadioSelect,
                                                                         label=bboolean[i].fieldName + '*',
                                                                         help_text=bboolean[i].promtInfo,
                                                                         initial=initvalue)
            else:
                bbooleannames['bboolean%s' % i] = forms.TypedChoiceField(required=False, coerce=lambda x: x == 'True',
                                                                         choices=((False, 'False'), (True, 'True')),
                                                                         widget=forms.RadioSelect,
                                                                         label=bboolean[i].fieldName,
                                                                         help_text=bboolean[i].promtInfo,
                                                                         initial=initvalue)
        # 枚举类型的定义
        eenumnames = locals()
        for i in xrange(0, eenumnum):
            choicess = [()]
            fill_topic_tree(parent_id=eenum[i].corrAttri, choicess=choicess)
            if (len(choicess[0]) != 0):
                initvalue = ''
                if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=eenum[i].id)) != 0):
                    initvalue = FileExtendInfo.objects.filter(fileId=id).get(fieldId=eenum[i].id).filedValue
                if (eenum[i].isMust):
                    eenumnames['eenum%s' % i] = forms.MultipleChoiceField(
                                                                  label=eenum[i].fieldName + '*',
                                                                  help_text='多选按Ctril键',
                                                                  choices=tree_choices(eenum[i].corrAttri),
                                                                  initial=initvalue)
                else:
                    eenumnames['eenum%s' % i] = forms.MultipleChoiceField(
                                                                  label=eenum[i].fieldName,
                                                                  help_text='多选按Ctril键',
                                                                  choices=kongtree_choices(eenum[i].corrAttri),
                                                                  initial=initvalue)

        # 树类型定义

        ttreenames = locals()
        global creatree
        creatree = []
        crealevel = []
        for i in xrange(0, ttreenum):
            sd = Category.objects.get(id=ttree[i].corrAttri)
            # while (sd.pid_id != 0):
            #     sd = sd.pid
            if (int(sd.id) == 273):
                target = Category.objects.get(id=int(ttree[i].corrAttri))
                with open('creatree.pkl', 'rb') as file:
                    ass = cPickle.load(file)
                    file.close()
                data = ass[0]
                level = ass[1]
                global levelist
                levelist = []
                for j in range(0, len(level)):
                    levelist.append('0_level_' + str(j))
                global creatree
                if (ttree[i].isMust):
                    creatree.append(
                        [ttree[i].fieldName, [levelist, json.dumps(data)], ttree[i].id, 1, ttree[i].promtInfo])
                else:
                    creatree.append(
                        [ttree[i].fieldName, [levelist, json.dumps(data)], ttree[i].id, 0, ttree[i].promtInfo])
            else:
                choicess = [()]
                fill_topic_tree(parent_id=ttree[i].corrAttri, choicess=choicess)
                if (len(choicess[0]) != 0):
                    initvalue = '49109'
                    if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=ttree[i].id)) != 0):
                        initvalue = FileExtendInfo.objects.filter(fileId=id).get(fieldId=ttree[i].id).filedValue
                        print 'ddddd',initvalue
                    if (ttree[i].isMust):
                        ttreenames['ttree%s' % i] = forms.MultipleChoiceField(
                            label=ttree[i].fieldName + '*',
                            help_text='多选按Ctril键',
                            choices=tree_choices(ttree[i].corrAttri),initial='49109',required=True)
                    else:
                        ttreenames['ttree%s' % i] = forms.MultipleChoiceField(
                            label=ttree[i].fieldName,
                            help_text='多选按Ctril键',
                            choices=kongtree_choices(ttree[i].corrAttri), initial='49109',required=False)

    if req.method == 'POST':
            form = SujectThemeDynamicForm(req.POST)
            global sstr, iint, ffloat, ddate, bboolean, eenum, ttree
            global sstrnum, iintnum, ffloatnum, ddatenum, bbooleannum, eenumnum, ttreenum

            for i in range(0, sstrnum):
                if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=sstr[i].id)) == 0):
                    fileextendupdate = FileExtendInfo()
                    fileextendupdate.fileId = id
                    fileextendupdate.fieldId = sstr[i].id
                    fileextendupdate.filedValue = form['sstr%s' % i].value()
                    fileextendupdate.save()
                else:
                    fileextendupdate = FileExtendInfo.objects.filter(fileId=id).get(fieldId=sstr[i].id)
                    fileextendupdate.filedValue = form['sstr%s' % i].value()
                    fileextendupdate.save()
            for i in range(0, iintnum):
                if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=iint[i].id)) == 0):
                    fileextendupdate = FileExtendInfo()
                    fileextendupdate.fileId = id
                    fileextendupdate.fieldId = iint[i].id
                    fileextendupdate.filedValue = form['iint%s' % i].value()
                    fileextendupdate.save()
                else:
                    fileextendupdate = FileExtendInfo.objects.filter(fileId=id).get(fieldId=iint[i].id)
                    fileextendupdate.filedValue = form['iint%s' % i].value()
                    fileextendupdate.save()
            for i in range(0, ffloatnum):
                if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=ffloat[i].id)) == 0):
                    fileextendupdate = FileExtendInfo()
                    fileextendupdate.fileId = id
                    fileextendupdate.fieldId = ffloat[i].id
                    fileextendupdate.filedValue = form['ffloat%s' % i].value()
                    fileextendupdate.save()
                else:
                    fileextendupdate = FileExtendInfo.objects.filter(fileId=id).get(fieldId=ffloat[i].id)
                    fileextendupdate.filedValue = form['ffloat%s' % i].value()
                    fileextendupdate.save()
            for i in range(0, ddatenum):
                if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=ddate[i].id)) == 0):
                    fileextendupdate = FileExtendInfo()
                    fileextendupdate.fileId = id
                    fileextendupdate.fieldId = ddate[i].id
                    if (len(form['ddate%s' % i].value()) != 0):
                        createdate = str(form['ddate%s' % i].value()).split('/')
                        if (len(createdate) == 3):
                            fileextendupdate.filedValue = datetime.strptime(''.join(createdate), "%Y%m%d").date()
                            fileextendupdate.save()
                    else:
                        fileextendupdate.filedValue = form['ddate%s' % i].value()
                        fileextendupdate.save()
                else:
                    fileextendupdate = FileExtendInfo.objects.filter(fileId=id).get(fieldId=ddate[i].id)
                    if (len(form['ddate%s' % i].value()) != 0):
                        createdate = str(form['ddate%s' % i].value()).split('/')
                        if (len(createdate) == 3):
                            fileextendupdate.filedValue = datetime.strptime(''.join(createdate), "%Y%m%d").date()
                            fileextendupdate.save()
                    else:
                        fileextendupdate.filedValue = form['ddate%s' % i].value()
                        fileextendupdate.save()
            for i in range(0, bbooleannum):
                if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=bboolean[i].id)) == 0):
                    fileextendupdate = FileExtendInfo()
                    fileextendupdate.fileId = id
                    fileextendupdate.fieldId = bboolean[i].id
                    fileextendupdate.filedValue = form['bboolean%s' % i].value()
                    fileextendupdate.save()
                else:
                    fileextendupdate = FileExtendInfo.objects.filter(fileId=id).get(fieldId=bboolean[i].id)
                    fileextendupdate.filedValue = form['bboolean%s' % i].value()
                    fileextendupdate.save()
            for i in range(0, eenumnum):
                choicess = [()]
                fill_topic_tree(parent_id=eenum[i].corrAttri, choicess=choicess)
                if ((len(choicess[0]) != 0) and (len(form['eenum%s' % i].value()) != 0)):
                    if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=eenum[i].id)) == 0):
                        fileextendupdate = FileExtendInfo()
                        fileextendupdate.fileId = id
                        fileextendupdate.fieldId = eenum[i].id
                        fileextendupdate.filedValue = form['eenum%s' % i].value()
                        fileextendupdate.save()
                    else:
                        fileextendupdate = FileExtendInfo.objects.filter(fileId=id).get(fieldId=eenum[i].id)
                        fileextendupdate.filedValue = form['eenum%s' % i].value()
                        fileextendupdate.save()
            for i in range(0, ttreenum):
                sd = Category.objects.get(id=ttree[i].corrAttri)
                # while (sd.pid_id != 0):
                #     sd = sd.pid
                if (int(sd.id) == 273):
                    continue
                else:
                    choicess = [()]
                    fill_topic_tree(parent_id=ttree[i].corrAttri, choicess=choicess)
                    if ((len(choicess[0]) != 0) and len(form['ttree%s' % i].value()) != 0):
                        # FileExtendInfo.objects.filter(fileId=id).filter(fieldId=ttree[i].id).delete()
                        if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=ttree[i].id)) == 0):
                            for item in form['ttree%s' % i].value():
                                fileextendupdate = FileExtendInfo()
                                fileextendupdate.fileId = id
                                fileextendupdate.fieldId = ttree[i].id
                                fileextendupdate.filedValue = item
                                fileextendupdate.save()
                        else:
                            for item in form['ttree%s' % i].value():
                                fileextendupdate = FileExtendInfo.objects.filter(fileId=id).get(fieldId=ttree[i].id)
                                fileextendupdate.filedValue = item
                                fileextendupdate.save()

            global creatree
            for treei in range(0,len(creatree)):
            #     循环每颗树的层次
                for treej in range(len(creatree[treei][1][0])-1,-1,-1):
                    fieldId=creatree[treei][2]
                    filedvalue=req.POST.get('0_level_'+str(treej))
                    if(filedvalue):
                        if(len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=fieldId)) == 0):
                            fileextendupdate = FileExtendInfo()
                            fileextendupdate.fileId = id
                            fileextendupdate.fieldId = fieldId
                            fileextendupdate.filedValue = filedvalue
                            fileextendupdate.save()
                        else:
                            fileextendupdate = FileExtendInfo.objects.filter(fileId=id).get(fieldId=fieldId)
                            fileextendupdate.filedValue = filedvalue
                            fileextendupdate.save()
                        break
            # 添加成功跳转
            messages.info(req, '专题文献修改成功')
            return redirect(r'../../../filebaseinfo/', {})

    try:
        form = SujectThemeDynamicForm()
        global editkuozhanshuxing
        print 'bbbbbbbbb',editkuozhanshuxing
        global creatree
    except View.DoesNotExist:
        return render_to_response('xadmin/404.html', {})
    return render_to_response('xadmin/himalaya/filebaseinfo/fileextendinfoupdate.html',
                              {'form': form,'editkuozhanshuxing':editkuozhanshuxing,'username':req.user, 'data':creatree})

# 文献的detail
def filebasedetail(req, id):
    form = FileBaseInfo.objects.get(id=int(id))
    lenpub=0
    if form.pubDate is None:
        lenpub=0
    else:
        lenpub=4
    formatdict = form.fileFormat.values('formatTypeName')
    strformat = ''
    i = 1
    for dd in formatdict:
        for key, value in dd.items():
            if (i == len(formatdict)):
                strformat += value
            else:
                strformat += value + ','
            i=i+1
    filetypedict = form.fileType.values('fileTypeName')
    strfiletype = ''
    i = 1
    for dd in filetypedict:
        for key, value in dd.items():
            if (i == len(filetypedict)):
                strfiletype += value
            else:
                strfiletype += value + ','
            i = i + 1
    landict = form.language.values('lanTypeName')
    strlan = ''
    i = 1
    for dd in landict:
        for key, value in dd.items():
            if (i == len(landict)):
                strlan += value
            else:
                strlan += value + ','
            i = i + 1
    disdict = form.discipline.values('disciplineTypeName')
    strdis = ''
    i = 1
    for dd in disdict:
        for key, value in dd.items():
            if (i == len(disdict)):
                strdis += value
            else:
                strdis += value + ','
            i = i + 1
    spatialdict = form.spatial.values('spcaeTypeName')
    strspatial = ''
    i = 1
    for dd in spatialdict:
        for key, value in dd.items():
            if (i == len(spatialdict)):
                strspatial += value
            else:
                strspatial += value + ','
            i = i + 1
    fileherf = r'/media/' + form.attachment.name.encode("UTF-8")
    picherf = r'/media/' + form.picture.name.encode("UTF-8")

    if (form.subjecttype == -1):

        return render_to_response('xadmin/himalaya/filebaseinfo/detail.html',
                                  {'form': form, 'strfiletype': strfiletype, 'strlan': strlan, 'strdis': strdis,
                                   'strspatial': strspatial,
                                   'strformat': strformat, 'fileherf': fileherf, 'picherf': picherf,'lenpub':lenpub,'username':req.user})
    else:
        formkey=[]
        formvalue=[]
        for item in SubjectTheme.objects.filter(subjectId=form.subjecttype):
            formkey.append(item.fieldName)
            name = ''
            if(int(item.fieldType)==5 or int(item.fieldType)==6):
                for index,value in enumerate(FileExtendInfo.objects.filter(fileId=id,fieldId=item.id)):
                    temp = Category.objects.get(id=int(value.filedValue))
                    name = name +temp.attrName
                    if(index<FileExtendInfo.objects.filter(fileId=id,fieldId=item.id).count()-1):
                        name = name + ','
                formvalue.append(name)
            else:
                try:
                    value = FileExtendInfo.objects.get(fileId=id, fieldId=item.id)
                    name = value.filedValue
                except Exception:
                    pass
                formvalue.append(name)
        #     formextkey.append(SubjectTheme.objects.get(id=int(dd.fieldId)).fieldName)
        #     if(((dd.filedValue=='-1') and (int(SubjectTheme.objects.get(id=int(dd.fieldId)).fieldType)==5)) or
        #            ((dd.filedValue == '-1') and (int(SubjectTheme.objects.get(id=int(dd.fieldId)).fieldType) == 6))):
        #         formextval.append('null')
        #     elif((int(SubjectTheme.objects.get(id=int(dd.fieldId)).fieldType)==5) or (int(SubjectTheme.objects.get(id=int(dd.fieldId)).fieldType)==6)):
        #         formextval.append(Category.objects.get(id=int(dd.filedValue)))
        #     else:
        #         formextval.append(dd.filedValue)
        # formextenddetail=zip(formextkey,formextval)
        formext = zip(formkey,formvalue)
        return render_to_response('xadmin/himalaya/filebaseinfo/detail.html',
                              {'form': form, 'formextenddetail':formext,'strfiletype': strfiletype, 'strlan': strlan, 'strdis': strdis,
                               'strspatial': strspatial,
                               'strformat': strformat, 'fileherf': fileherf, 'picherf': picherf,'lenpub':lenpub,'username':req.user})



# 解压自拍文档
def unzip_file(zipfilename, unziptodir):
    if not os.path.exists(unziptodir): os.mkdir(unziptodir, 0777)
    zfobj = zipfile.ZipFile(zipfilename)
    for name in zfobj.namelist():
        name = name.replace('\\', '/')

        if name.endswith('/'):
            os.mkdir(os.path.join(unziptodir, name))
        else:
            ext_filename = os.path.join(unziptodir, name)
            ext_dir = os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir): os.mkdir(ext_dir, 0777)
            outfile = open(ext_filename, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()


# 1:精确查找
# 定义全局变量
def search(path, word):
    for filename in os.listdir(path):
        fp = os.path.join(path, filename)
        if os.path.isfile(fp) and word in filename:
            global viewpathstr
            viewpathstr = fp
        elif os.path.isdir(fp):
            search(fp, word)


# view的添加页面
def viewadd(req):
    if req.method == 'POST':
        form = ViewForm(req.POST, req.FILES)
        if form.is_valid():
            viewi = View()
            viewi.viewName = form['viewName'].value()
            l = str(form['createDate'].value()).split('/')
            viewi.createDate = datetime.strptime(''.join(l), "%Y%m%d").date()
            viewi.viewIntro = form['viewIntro'].value()
            viewi.viewPic = form['viewPic'].value()
            viewi.viewEqu = form['viewEqu'].value()
            viewi.viewPath = form['viewPath'].value()
            viewi.viewAuth = form['viewAuth'].value()
            viewi.viewPlace = form['viewPlace'].value()# 解压需要的文件名
            s1 = default_storage.save('himalaya/quanjing/' + viewi.viewPath.name, ContentFile(viewi.viewPath.read()))
            filename = r'./media/' + str(s1)# 解压需要放的路径,l[0]表示去掉扩展名的文件路径
            unzip_file(filename, './media/himalaya/quanjing/')# 解压
            # 查找Index.Html路径
            global viewpathstr
            viewpathstr = None
            search('./media/'+(str(s1).split('.'))[0], 'index.html')  # 获取到的路径：类似./media/himalaya/quanjing/Jiuzhaigou_W74ssR2\output\index.html
            if viewpathstr==None:
                messages.info(req, '全景异常,请重新上传!')
                return redirect('..', {})
            viewi.viewPath.name = viewpathstr.split('media/')[1].replace('\\', r'/')
            viewi.save()
            messages.info(req, '保存成功')
            return redirect('..', {})
    else:
        form = ViewForm()
    return render_to_response('xadmin/himalaya/view/add.html', {'form': form,'username':req.user})


# view的修改页面
def viewedite(req, id):
    if req.method == 'POST':
            formnew = ViewForm(req.POST, req.FILES)
            viewupdate = View.objects.get(id=int(id))
            viewupdate.viewName = formnew['viewName'].value()
            viewupdate.viewEqu = formnew['viewEqu'].value()
            viewupdate.viewAuth = formnew['viewAuth'].value()
            viewupdate.viewPlace = formnew['viewPlace'].value()
            viewupdate.viewIntro = formnew['viewIntro'].value()
            createdate = str(formnew['createDate'].value()).split('/')
            if (len(createdate) == 3):
                viewupdate.createDate = datetime.strptime(''.join(createdate), "%Y%m%d").date()
            if formnew['viewPath'].value():
                ss = formnew['viewPath'].value()
                s1 = default_storage.save('himalaya/quanjing/' + str(ss),ContentFile(ss.read()))
                filename = r'./media/' + str(s1)
                unzip_file(filename, './media/himalaya/quanjing/')
                global viewpathstr
                viewpathstr = None
                search('./media/' + (str(s1).split('.'))[0],'index.html')
                if viewpathstr == None:
                    if (os.path.exists('./media/' + (str(s1).split('.'))[0])):
                        shutil.rmtree('./media/' + (str(s1).split('.'))[0])
                    if (os.path.exists('./media/' + str(s1))):
                        os.remove('./media/' + str(s1))
                    messages.info(req, '全景异常,请重新编辑!')
                    return redirect('../..', {})
                s = viewupdate.viewPath
                s = str(s).split("/")
                str1 = s[0:3]
                str1 = '/'.join(str1)
                str1 = str1.decode('utf-8')
                if(os.path.exists('./media/' + str1)):
                    shutil.rmtree('./media/' + str1)
                if (os.path.exists('./media/' + str1 + '.zip')):
                    os.remove('./media/' + str1 + '.zip')
                viewupdate.viewPath.name = viewpathstr.split('media/')[1].replace('\\', r'/')
            if formnew['viewPic'].value():
                s1 = viewupdate.viewPic
                s1 = str(s1)
                s1 = s1.decode('utf-8')
                if(os.path.exists('./media/' + str(s1))):
                    os.remove('./media/' + str(s1))
                viewupdate.viewPic = formnew['viewPic'].value()
            viewupdate.save()
            messages.info(req, '修改成功')
            return redirect('../..', {})
    try:
        form = View.objects.get(id=int(id))
        fileherf = r'/media/' + form.viewPath.name.encode("UTF-8")
        picherf = r'/media/' + form.viewPic.name.encode("UTF-8")
    except View.DoesNotExist:
        return render_to_response('xadmin/404.html', {})
    return render_to_response('xadmin/himalaya/view/update.html',
                              {'form': form, 'picherf': picherf, 'fileherf': fileherf,'username':req.user})






def check_tree(id):
    global flag
    flag = False
    try:
        s=SubjectTheme.objects.get(corrAttri=id)
        global flag
        flag = True
        return flag
    except:
        ts = Category.objects.filter(pid_id=id)
        for t in ts:
            check_tree(t.id)

def check_ptree(id):
    global flag1
    flag1 = False
    t = FileExtendInfo.objects.filter(filedValue=id)
    for x in t:
        str = SubjectTheme.objects.get(id = x.fieldId)
        if(int(str.fieldType) == 6):
            global flag1
            flag1 = True
    return flag1


@ajax
def Category_data_upload(request):
    opt = request.POST.get('opt')
    if opt == '0':
        name = request.POST.get('name')
        idnum = request.POST.get('id')
        item = Category.objects.get(id=idnum)
        item.attrName=name
        item.save()

    if opt== '1':
        idnum = request.POST.get('id')
        Category.objects.filter(id=int(idnum)).delete()

    if opt=='2':
        name = request.POST.get('name')
        pname = request.POST.get('pname')
        try:
            Category.objects.get(attrName=name, pid_id=int(pname))
            return HttpResponse(json.dumps({"data": "-2"}))
        except ObjectDoesNotExist:
            data = Category(attrName=name,pid_id=int(pname))
            data.save()
            while(data.pid_id!=0):
                data = Category.objects.get(id = data.pid_id)
            if(data.id==273 ):
                global level
                level = 1
                data = getdata(data,1)
                global levelist
                levelist = []
                for i in range(0,level):
                    levelist.append('level_'+str(i))
                with open('creatree.pkl','w+b') as file:
                    cPickle.dump((data,levelist),file)
                    file.close()
            data = Category.objects.get(attrName=name, pid_id=int(pname))
            id = data.id
            return HttpResponse(json.dumps({"data": id}))

    if opt == '3':
        name = request.POST.get('name')
        pname = request.POST.get('id')
        try:
            Category.objects.get(attrName=name, pid_id=int(pname))
            return HttpResponse(json.dumps({"data": "-2"}))
        except ObjectDoesNotExist:
            data = Category(attrName=name, pid_id=int(pname))
            data.save()
            while (data.pid_id != 0):
                data = Category.objects.get(id=data.pid_id)
            if (data.id == 273 ):
                print 'ssss'
                global level
                level = 1
                data = getdata(data, 1)
                global levelist
                levelist = []
                for i in range(0, level):
                    levelist.append('level_' + str(i))
                with open('creatree.pkl', 'w+b') as file:
                    cPickle.dump((data, levelist), file)
                    file.close()
            data = Category.objects.get(attrName=name, pid_id=int(pname))
            id = data.id
            return HttpResponse(json.dumps({"data": id}))

    if opt == '4':
        idnum = request.POST.get('id')
        check_tree(int(idnum))
        check_ptree(int(idnum))
        global flag
        global flag1
        if flag == True or flag1 == True:
            return HttpResponse(json.dumps({"data": "-2"}))
        else:
            return HttpResponse(json.dumps({"data": "0"}))


@ajax
def subjecttheme_category(request):
	data = CategorySerializer(Category.objects.all(),many=True).data
	data = JSONRenderer().render(data)
	return HttpResponse(json.dumps(data))

def category(request):
	data = CategorySerializer(Category.objects.all(),many=True).data
	data = JSONRenderer().render(data)
	return render(request,"xadmin/himalaya/category.html",{"data":json.dumps(data),'username':request.user})

def subjecttheme_add(request):
    data = CategorySerializer(Category.objects.all(), many=True).data
    data = JSONRenderer().render(data)
    # d = FileBaseInfo.objects.filter(subjecttype=int(id))
    # if (d.count() != 0):
    #     html = "<html><script>alert('已有文献使用，无法编辑')</script></html>"
    #     return HttpResponse(html)
    if request.method == 'POST':
        form = SujectThemeForm(request.POST)
        if form.is_valid():
            st=SubjectTheme()
            st.fieldName=form['fieldName'].value()
            st.fieldType=form['fieldType'].value()
            st.promtInfo=form['promtInfo'].value()
            st.isMust=form['isMust'].value()
            st.isPrompt=form['isPrompt'].value()
            st.subjectId_id=form['qiantaiid'].value()
            st.corrAttri = form['treenum'].value()
            st.save()
            if(int(st.fieldType)==6):
                sd = Category.objects.get(id = st.corrAttri)
                while(sd.pid_id!=0):
                    sd = sd.pid
                if(int(st.fieldType)==6 and int(sd.id) == 273):
                    global level
                    level = 1
                    data = getdata(Category.objects.get(id = st.corrAttri), 1)
                    global levelist
                    levelist = []
                    for i in range(0, level):
                        levelist.append('level_' + str(i))
                    with open(str(st.id)+'_creatree.pkl', 'w+b') as file:
                        cPickle.dump((data, levelist), file)
                        file.close()
            return redirect('..'+'?_rel_subjectId__id__exact='+form['qiantaiid'].value(),{})
    else:
        form=SujectThemeForm()
    return render_to_response("xadmin/himalaya/subjecttheme/add.html",{'form':form,"data": json.dumps(data),'username':request.user})

def tree_update(request,id):
    data = CategorySerializer(Category.objects.all(), many=True).data
    data = JSONRenderer().render(data)
    return render_to_response("xadmin/himalaya/category.html", {"data": json.dumps(data)})

def subjecttheme_update(request,id):
    data1 = CategorySerializer(Category.objects.all(), many=True).data
    data1 = JSONRenderer().render(data1)
    data = SubjectTheme.objects.get(id=int(id))
    #d = FileExtendInfo.objects.filter(fieldId=int(data.fieldType))
    # if (d.count() != 0):
    #     html = "<html><script>alert('已有文献使用，无法编辑')</script></html>"
    #     # return HttpResponse(html),redirect('../../'+'?_rel_subjectId__id__exact='+str(data.subjectId_id),{})
    #     return HttpResponse(html)
    if request.method == 'POST':
        form = SujectThemeForm(request.POST)
        if form.is_valid():
            if (form['fieldType'].value() == '6'):
                corr = form['treenum'].value()
                sd = Category.objects.get(id=corr)
                # while (sd.pid_id != 0):
                #     sd = sd.pid
                if (int(sd.id) == 273):
                    global level
                    level = 1
                    data = getdata(Category.objects.get(id=corr), 1)
                    global levelist
                    levelist = []
                    for i in range(0, level):
                        levelist.append('level_' + str(i))
                    print '4444444444444id', id
                    with open('creatree.pkl', 'w+b') as file:
                        cPickle.dump((data, levelist), file)
                        file.close()
            else:
                corr = -1
            SubjectTheme.objects.filter(id=int(id)).update(fieldName=form['fieldName'].value(),
                                                        fieldType=form['fieldType'].value(),
                                                        promtInfo=form['promtInfo'].value(),
                                                        isMust=form['isMust'].value(),
                                                        isPrompt=form['isPrompt'].value(),
                                                        subjectId=form['qiantaiid'].value(),
                                                        corrAttri=corr)
            return redirect('../../'+'?_rel_subjectId__id__exact='+form['qiantaiid'].value(),{})
    else:
        form = SujectThemeForm()
    return render_to_response("xadmin/himalaya/subjecttheme/subjecttheme_update.html", {"data": data, "data1": json.dumps(data1),'username':request.user})



def swfupload(request,dynamicfilebaseid):
    if request.method == 'POST':
        s = request.FILES.get('attachment')
        st = s.name
        path = default_storage.save('./himalaya/swfupload/'+st,ContentFile(s.read()))
        #os.path.join(settings.MEDIA_ROOT, path)
        # path = './media/himalaya/swfupload/' + str(st)
        request.session['path'] = os.path.join('./media',path)
        request.session['dynamicfilebaseid'] = dynamicfilebaseid
        if (request.POST.get("select") == 'modify'):
            return redirect(r"../../swfmodify/")
        else:
            return redirect("../../swfchoice/")
    return render_to_response("xadmin/himalaya/filebaseinfo/swfupload.html")


def swfmodify(request):
    path = request.session.get('path')
    dynamicfilebaseid = request.session.get('dynamicfilebaseid')
    ss = xlrd.open_workbook(path)
    table = ss.sheets()[0]
    data = table.row_values(0)
    fields = FileBaseInfo._meta.get_fields()
    value = [('', '---------')]
    basic = []
    extend = []
    for i in range(0,len(data)):
        value.append((i,data[i]))
    for field in fields:
        if (field.name != 'subjecttype' and field.name != 'id' and field.name != 'uploadDate' and field.name != 'updateDate' and field.name != 'size' and field.name != 'contentLength' and field.name!='picture' and field.name != 'attachment'):
            basic.append(field.verbose_name)
    dynamicfilebaseid = int(dynamicfilebaseid)
    if (dynamicfilebaseid == -1):
        pass
    else:
        feature = SubjectTheme.objects.filter(subjectId=dynamicfilebaseid)
        for field in feature:
            extend.append((field.id,field.fieldName))
    class basicForm(forms.Form):
        eenumnames = locals()
        for i in range(len(basic)):
            eenumnames['basic%s' % i] = forms.ChoiceField(label=basic[i],
                                                              choices=value,required=False)
        i = len(basic)
        eenumnames["basic%s" % i] = forms.FileField(label=u'缩略图',required=False,widget=TextInput(attrs={'type':'file','multiple':'multiple'}),
                                                    help_text=u'请上传缩略图!')
        i = i + 1
        eenumnames["basic%s" % i] = forms.FileField(label=u'附件', required=False,widget=TextInput(attrs={'type':'file','multiple':'multiple'}),
                                                    error_messages={'required':u'请上传附件!'},help_text=u'请上传附件!')
    class extendForm(forms.Form):
        extends =locals()
        for i in range(len(extend)):
            extends['extend%s' % i] = forms.ChoiceField(label=extend[i][1],
                                                          choices=value,required=False)
    if request.method =='POST':
        basicform = basicForm(request.POST, request.FILES)
        extendform = extendForm(request.POST)
        if basicform.is_valid() and extendform.is_valid():
            rangeLetter = ('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
            dict = []
            dict1 = []
            subjecttype = ''
            if(dynamicfilebaseid!=-1 and dynamicfilebaseid!=0):
                subject = Subject.objects.get(id=int(dynamicfilebaseid))
                subjecttype = subject.subjectName
                spath = os.path.normpath('./media/himalaya/files/'+subjecttype)
                if not os.path.exists(spath) or not os.path.isdir(spath):
                    os.mkdir('./media/himalaya/files/'+subjecttype)
                spath = os.path.normpath('./media/himalaya/images/'+subjecttype)
                if not os.path.exists(spath) or not os.path.isdir(spath):
                    os.mkdir('./media/himalaya/images/'+subjecttype)
            picturepath = -1
            attachpath = -1
            existimag = 1
            imagepath1 = ''
            attachpath2 = ''
            errorfile =[]
            errorpicture =[]
            # newFileName = random.choice(rangeLetter) + random.choice(rangeLetter) + time.strftime('%M%S',
            #                                                                                       time.localtime(
            #                                                                                         time.time()))
            # s = request.FILES.getlist('basic%s' % len(basic))
            # if s:
            #     os.mkdir('./media/himalaya/images/'+newFileName)
            #     for file in s:
            #         st = file.name
            #         imagepath = default_storage.save('himalaya/images/'+newFileName+'/'+st, ContentFile(file.read()))
            #         # print(os.path.abspath(imagepath))
            #     picturepath = 0
            # else:
            #     existimag = 0
            # s = request.FILES.getlist('basic%s' % (len(basic) + 1))
            # if s:
            #     os.mkdir('./media/himalaya/files/'+newFileName)
            #     for file in s:
            #         st = file.name
            #         attachpath1 = default_storage.save('himalaya/files/'+newFileName+'/'+st, ContentFile(file.read()))
            #     attachpath = 0
            repetition = []
            extenderror = {}
            manyerror = {}
            formaterror={}
            if(attachpath!=-2 and (picturepath!=-2 or existimag==0)):
                for i in range(len(basic)):
                    s = basicform['basic%s' % i].value()
                    dict.append(s)
                for i in range(len(extend)):
                    s = extendform['extend%s' % i].value()
                    dict.append(s)
                nrows = table.nrows
                for i in range(1, nrows):
                    if(table.cell(i, 0).value):
                        try:
                            fbi = FileBaseInfo.objects.get(filecode=table.cell(i, 0).value)
                            fbi.filecode = table.cell(i, 0).value
                            # 日期类型转换
                            date = None
                            p = u'[0-9]{4}年([0-9]{1,2}月)?([0-9]{1,2}日)?'
                            if dict[7] != '':
                                temstr = table.cell(i, int(dict[7])).value
                                if re.search(p, temstr):
                                    date = table.cell(i, int(dict[7])).value
                                    m = date.decode('utf-8').split(u"年".decode('utf-8'))
                                    year = m[0]
                                    if (len(m) > 1 and u"月".decode('utf-8') in m[1]):
                                        m = m[1].split(u"月".decode('utf-8'))
                                        month = m[0]
                                        if (len(m) > 1 and u"日".decode('utf-8') in m[1]):
                                            m = m[1].split(u"日".decode('utf-8'))
                                            day = m[0]
                                            date = str(year) + str(month) + str(day)
                                            date = datetime.strptime(''.join(date), "%Y%m%d").date()
                                        else:
                                            date = str(year) + str(month)
                                            date = datetime.strptime(''.join(date), "%Y%m").date()
                                    else:
                                        date = str(year)
                                        date = datetime.strptime(''.join(date), "%Y").date()
                                else:
                                    formaterror[table.cell(i, 0).value] = temstr
                                    continue
                            flag = 0
                            filetype = []
                            lang = []
                            disc = []
                            spa = []
                            fileFor = []
                            querylist = {}
                            if dict[11] != '':
                                values = str(table.cell(i, int(dict[11])).value).decode('utf-8')
                                values = re.split(u',|，', values)
                                #多对多的删除
                                for item in values:
                                    try:
                                        fileType = FileType.objects.get(fileTypeName=item.strip())
                                        filetype.append(fileType)
                                    except:
                                        manyerror[fbi.filecode] = item
                                        flag = 1
                                        break
                            if dict[12] != '' and flag == 0:
                                values = str(table.cell(i, int(dict[12])).value).decode('utf-8')
                                values = re.split(u',|，', values)
                                for item in values:
                                    try:
                                        language = Language.objects.get(lanTypeName=item.strip())
                                        lang.append(language)
                                    except:
                                        manyerror[fbi.filecode] = item
                                        flag = 1
                                        break
                            if dict[13] != '' and flag == 0:

                                values = str(table.cell(i, int(dict[13])).value).decode('utf-8')
                                values = re.split(u',|，', values)
                                for item in values:
                                    try:
                                        discipline = Discipline.objects.get(disciplineTypeName=item.strip())
                                        disc.append(discipline)
                                    except:
                                        manyerror[fbi.filecode] = item
                                        flag = 1
                                        break
                            if dict[14] != '' and flag == 0:

                                values = str(table.cell(i, int(dict[14])).value).decode('utf-8')
                                values = re.split(u',|，', values)
                                for item in values:
                                    try:
                                        spatial = SpaceScope.objects.get(spcaeTypeName=item.strip())
                                        spa.append(spatial)
                                    except:
                                        manyerror[fbi.filecode] = item
                                        flag = 1
                                        break
                            if dict[15] != '' and flag == 0:
                                values = str(table.cell(i, int(dict[15])).value).decode('utf-8')
                                values = re.split(u',|，', values)
                                for item in values:
                                    try:
                                        fileFormat = Format.objects.get(formatTypeName=item.strip())
                                        fileFor.append(fileFormat)
                                    except:
                                        manyerror[fbi.filecode] = item
                                        flag = 1
                                        break
                            if flag == 0:
                                for j in range(len(basic), len(basic) + len(extend)):
                                    item = extend[j - len(basic)][0]
                                    FileExtendInfo.objects.filter(fileId=fbi.id, fieldId=item).delete()
                                    if (dict[j]!='' and table.cell(i,int(dict[j])).value!='' and flag==0):
                                        if (int(SubjectTheme.objects.get(id=int(item)).fieldType) == 6 or int(
                                                SubjectTheme.objects.get(id=int(item)).fieldType) == 5):
                                            values = str(table.cell(i, int(dict[j])).value).decode('utf-8')
                                            values = re.split(u',|，', values)
                                            fid = []
                                            for val in values:
                                                pid = SubjectTheme.objects.get(id=int(item)).corrAttri
                                                global featureid
                                                featureid = None
                                                checktrees(int(pid), val.strip())
                                                if featureid != None:
                                                    fid.append(featureid)
                                                else:
                                                    extenderror[fbi.filecode] = val
                                                    flag = 1
                                                    break
                                            querylist[item] = fid
                                        else:
                                            values = str(table.cell(i, int(dict[j])).value).decode('utf-8')
                                            values = re.split(u',|，', values)
                                            fid = []
                                            for val in values:
                                                fid.append(val)
                                            querylist[item] = fid
                            if flag == 0:
                                # # 图片匹配，文件匹配
                                # temflag = 0
                                # fileLength = None
                                # filesize = ''
                                # pic = 'himalaya/images'
                                # att = 'himalaya/files'
                                # sstr1 = ''
                                # if (existimag == 1):
                                #     temflag = 1
                                #     sstr1 = glob.glob('./media/himalaya/images/' + newFileName + '/' + str(
                                #         table.cell(i, 0).value).strip() + '.*')
                                #     if len(sstr1) != 0:
                                #         pic = os.path.join('himalaya/images', subjecttype, os.path.basename(sstr1[0]))
                                #     else:
                                #         errorpicture.append(str(table.cell(i, 0).value).strip())
                                #         continue
                                # sstr2 = glob.glob('./media/himalaya/files/' + newFileName + '/' + str(
                                #     table.cell(i, 0).value).strip() + '.*')
                                # if (attachpath == 0):
                                #     if len(sstr2) != 0:
                                #         filesize = getsize(sstr2[0])
                                #         att = os.path.join('himalaya/files', subjecttype, os.path.basename(sstr2[0]))
                                #         filename = os.path.basename(sstr2[0])
                                #         str1 = filename.split('.')
                                #         if (str1[1] == 'pdf'):
                                #             try:
                                #                 pdf = PdfFileReader(open(sstr2[0], "r"))
                                #                 fileLength = pdf.getNumPages()
                                #                 if (existimag == 0):
                                #                     output = PdfFileWriter()
                                #                     output.addPage(pdf.getPage(0))
                                #                     outputStrem = open(
                                #                         './media/himalaya/images/' + subjecttype + '/' + str1[
                                #                             0] + '.pdf',
                                #                         'w')
                                #                     output.write(outputStrem)
                                #                     outputStrem.close()
                                #                     pic = 'himalaya/images/' + subjecttype + '/' + str1[0] + '.jpg'
                                #                     with Image(
                                #                             filename='./media/himalaya/images/' + subjecttype + '/' +
                                #                                     str1[
                                #                                         0] + '.pdf') as pdf:
                                #                         with pdf.convert('jpg') as image:
                                #                             image.save(
                                #                                 filename='./media/himalaya/images/' + subjecttype + '/' +
                                #                                          str1[
                                #                                              0] + '.jpg')
                                #                     os.remove(
                                #                         './media/himalaya/images/' + subjecttype + '/' + str1[
                                #                             0] + '.pdf')
                                #             except Exception:
                                #                 errorfile.append(str(table.cell(i, 0).value).strip())
                                #                 continue
                                #         if (os.path.exists(os.path.join('./media/himalaya/files', subjecttype,
                                #                                         os.path.basename(sstr2[0])))):
                                #             os.remove(os.path.join('./media/himalaya/files', subjecttype,
                                #                                    os.path.basename(sstr2[0])))
                                #         shutil.move(sstr2[0], './media/himalaya/files/' + subjecttype)
                                #     else:
                                #         errorfile.append(str(table.cell(i, 0).value).strip())
                                #         continue
                                # if (existimag == 1):
                                #     shutil.move(sstr1[0], './media/himalaya/images/' + subjecttype)
                                emflag = 0
                                if dict[1] != '':
                                    emflag = 1
                                    fbi.title = table.cell(i, int(dict[1])).value
                                if dict[2] != '':
                                    emflag = 1
                                    fbi.creator = table.cell(i, int(dict[2])).value
                                if dict[3] != '':
                                    emflag = 1
                                    fbi.keywords = table.cell(i, int(dict[3])).value
                                if dict[4] != '':
                                    fbi.description = table.cell(i, int(dict[4])).value
                                if dict[5] != '':
                                    emflag = 1
                                    fbi.publisher = table.cell(i, int(dict[5])).value
                                if dict[6] != '':
                                    emflag = 1
                                    fbi.contributor = table.cell(i, int(dict[6])).value
                                if dict[7] != '':
                                    emflag = 1
                                    fbi.pubDate = date
                                if dict[8] != '':
                                    emflag = 1
                                    fbi.uploadPeople = table.cell(i, int(dict[8])).value
                                if dict[9] != '':
                                    emflag = 1
                                    fbi.notes = table.cell(i, int(dict[9])).value
                                if dict[10] != '':
                                    emflag = 1
                                    fbi.check = False if table.cell(i, int(
                                        dict[10])).value == 'False' else True
                                # if attachpath == 0:
                                #     emflag = 1
                                #     fbi.attachment = att
                                #     fbi.size = filesize
                                #     fbi.contentLength = fileLength
                                # if picturepath == 0:
                                #     emflag = 1
                                #     fbi.picture = pic
                                if (len(filetype) != 0):
                                    emflag = 1
                                    for item in filetype:
                                        fbi.fileType.add(item)
                                if (len(lang) != 0):
                                    emflag = 1
                                    for item in lang:
                                        fbi.language.add(item)
                                if (len(disc) != 0):
                                    emflag = 1
                                    for item in disc:
                                        fbi.discipline.add(disc)
                                if (len(spa) != 0):
                                    emflag = 1
                                    for item in spa:
                                        fbi.spatial.add(item)
                                if (len(fileFor) != 0):
                                    emflag = 1
                                    for item in fileFor:
                                        fbi.fileFormat.add(item)
                                if(emflag==1):
                                    fbi.save()
                                query = []
                                for key,temval in querylist.items():
                                    for value in temval:
                                        query.append(FileExtendInfo(fileId=fbi.id, fieldId=key, filedValue=value))
                                if(len(query)!=0):
                                    FileExtendInfo.objects.bulk_create(query)
                                print(fbi.filecode, 'success')
                        except ObjectDoesNotExist:
                            repetition.append(str(table.cell(i, 0).value))
            # if(attachpath==0):
            #     shutil.rmtree('./media/himalaya/files/'+newFileName)
            # if(picturepath==0):
            #     shutil.rmtree('./media/himalaya/images/'+newFileName)
            if(len(repetition)!=0 or len(errorfile)!=0 or len(extenderror)!=0 or len(manyerror)!=0 or len(errorpicture)!=0) or attachpath==-2 or picturepath==-2 or len(formaterror)!=0:
                request.session['repetiton'] = repetition
                request.session['errorfile'] = errorfile
                request.session['errorpicture'] = errorpicture
                request.session['extenderror'] = extenderror
                request.session['manyerror'] = manyerror
                request.session['attachpath'] = attachpath2
                request.session['picturepath'] = imagepath1
                request.session['formaterror'] = formaterror
                return redirect('/xadmin/himalaya/modifyaddr/')
            else:
                return redirect('../')
    else:
        basicform = basicForm()
        extendform = extendForm()
    return render_to_response("xadmin/himalaya/filebaseinfo/swfchoice.html",{"basicform": basicForm,"extendform":extendform})

# def swfmodify(request):
#     path = request.session.get('path')
#     dynamicfilebaseid = request.session.get('dynamicfilebaseid')
#     ss = xlrd.open_workbook(path)
#     table = ss.sheets()[0]
#     data = table.row_values(0)
#     fields = FileBaseInfo._meta.get_fields()
#     many = FileBaseInfo._meta.many_to_many
#     value = [('-1', '---------')]
#     flage = {}
#     flage['-1'] = -1
#     fextend = ''
#     for field in fields:
#         if (field.name != 'subjecttype' and field.name != 'id' and field.name != 'uploadDate' and field.name != 'updateDate' and field.name != 'size' and field.name != 'contentLength'):
#             flage[field.name] = 0
#             value.append((field.name, field.verbose_name))
#     for field in many:
#         flage[field.name] = 2
#         value.append((field.name, field.verbose_name))
#     dynamicfilebaseid = int(dynamicfilebaseid)
#     if (dynamicfilebaseid == -1):
#         pass
#     else:
#         extend = SubjectTheme.objects.filter(subjectId=dynamicfilebaseid)
#         for field in extend:
#             value.append((field.id, field.fieldName))
#             flage[str(field.id)] = 1
#
#     class swfForm(forms.Form):
#         eenumnames = locals()
#         eenum = len(data)
#         for i in range(len(data)):
#             eenumnames['data%s' % i] = forms.ChoiceField(label=data[i],
#                                                          choices=value)
#         i = len(data)
#         eenumnames["data%s" % i] = forms.FileField(label=u'缩略图')
#         i = i + 1
#         eenumnames["data%s" % i] = forms.FileField(label=u'附件')
#
#     if request.method == 'POST':
#         form = swfForm(request.POST, request.FILES)
#         dict = []
#         if (dynamicfilebaseid != -1 and dynamicfilebaseid != 0):
#             subject = Subject.objects.get(id=int(dynamicfilebaseid))
#             subjecttype = subject.subjectName
#             spath = os.path.normpath('./media/himalaya/files/' + subjecttype)
#             if not os.path.exists(spath) or not os.path.isdir(spath):
#                 os.mkdir('./media/himalaya/files/' + subjecttype)
#             spath = os.path.normpath('./media/himalaya/images/' + subjecttype)
#             if not os.path.exists(spath) or not os.path.isdir(spath):
#                 os.mkdir('./media/himalaya/images/' + subjecttype)
#         s = request.FILES.get('data%s' % len(data))
#         errorfile = []
#         errorpicture = []
#         picturepath = -1
#         attachpath = -1
#         imagepath1 = -1
#         attachpath2 = -1
#         if s:
#             st = s.name
#             imagepath = default_storage.save('himalaya/images/' + str(st), ContentFile(s.read()))
#             # if(GetFileNameAndExt(imagepath)=='rar'):
#             #     # file = rarfile.RarFile(imagepath)  # 这里写入的是需要解压的文件，别忘了加路径
#             #     # file.extractall('./media/himalaya/images/'+subjecttype)
#             # if (GetFileNameAndExt(imagepath) == 'zip'):
#             if (os.path.isfile('./media/' + imagepath)):
#                 f = zipfile.ZipFile('./media/' + imagepath, 'r')
#                 if(f.testzip()==None):
#                     for file in f.namelist():
#                         f.extract(file, './media/himalaya/images/')
#                     picturepath = './media/himalaya/images/' + f.namelist()[0]
#                 else:
#                     picturepath = -2
#                     imagepath1 = st
#                 os.remove('./media/' + imagepath)
#             else:
#                 print 'not found'
#         s = request.FILES.get('data%s' % (len(data) + 1))
#         if s:
#             st = s.name
#             attachpath1 = default_storage.save('./himalaya/files/' + str(st), ContentFile(s.read()))
#             # if (GetFileNameAndExt(attachpath) == 'rar'):
#             #     file = rarfile.RarFile(attachpath)  # 这里写入的是需要解压的文件，别忘了加路径
#             #     file.extractall('./media/himalaya/files/' + subjecttype)
#             # if (GetFileNameAndExt(attachpath) == 'zip'):
#             if (os.path.isfile('./media/' + attachpath1)):
#                 f = zipfile.ZipFile('./media/' + attachpath1, 'r')
#                 if(f.testzip()==None):
#                     for file in f.namelist():
#                         f.extract(file, './media/himalaya/files/')
#                     attachpath = './media/himalaya/files/' + f.namelist()[0]
#                 else:
#                     attachpath=-2
#                     attachpath2 = st
#                 os.remove('./media/' + attachpath1)
#             else:
#                 print 'not found'
#         repetition = []
#         manyerror = {}
#         extenderror = {}
#         if(attachpath!=-2 and picturepath!=-2):
#             for i in range(len(data)):
#                 s = form['data%s' % i].value()
#                 dict.append(s)
#             nrows = table.nrows
#             for i in range(1, nrows):
#                 if (table.cell(i, 0).value):
#                     try:
#                         fbi = FileBaseInfo.objects.get(filecode=table.cell(i, 0).value)
#                         extend = {}
#                         manytomany = {}
#                         for j in range(len(data)):
#                             s = dict[j]
#                             if (s!=-1):
#                                 if (int(flage[s]) == 0):
#                                     # mt = fbi._meta.get_field(s)
#                                     if (type(fbi._meta.get_field(s)) == django.db.models.fields.DateField):
#                                         date = table.cell(i, j).value
#                                         m = date.decode('utf-8').split(u"年".decode('utf-8'))
#                                         year = m[0]
#                                         if (len(m) > 1 and u"月".decode('utf-8') in m[1]):
#                                             m = m[1].split(u"月".decode('utf-8'))
#                                             month = m[0]
#                                             if (len(m) > 1 and u"日".decode('utf-8') in m[1]):
#                                                 m = m[1].split(u"日".decode('utf-8'))
#                                                 day = m[0]
#                                             else:
#                                                 day = '01'
#                                         else:
#                                             month = '01'
#                                             day = '01'
#                                         date = str(year) + str(month) + str(day)
#                                         date = datetime.strptime(''.join(date), "%Y%m%d").date()
#                                         setattr(fbi, s, date)
#                                     else:
#                                         setattr(fbi, s, table.cell(i, j).value)
#                                         fbi.save()
#                                 elif (int(flage[s]) == 1):
#                                     extend[s] = table.cell(i, j).value
#                                 elif (int(flage[s]) == 2):
#                                     manytomany[s] = table.cell(i, j).value
#                         flagp = 0
#                         if(attachpath!=-1):
#                             for file in os.listdir(attachpath):
#                                 sstr1 = os.path.join('./media/himalaya/files/', subjecttype, file)
#                                 str1 = file.split('.')
#                                 if (str(str1[0]) == table.cell(i, 0).value):
#                                     flagp = 1
#                                     sourcecpy(os.path.join(attachpath, file), './media/himalaya/files/' + subjecttype)
#                                     fbi.attachment = 'himalaya/files/' + subjecttype + '/' + file
#                                     fbi.size = os.path.getsize(sstr1)
#                                     if (str1[1] == 'pdf'):
#                                         pdf = PdfFileReader(open(sstr1, "r"))
#                                         fbi.contentLength = pdf.getNumPages()
#                                     fbi.save()
#                             if (flagp == 0):
#                                 errorfile.append(fbi.filecode)
#                         flagp = 0
#                         if(picturepath!=-1):
#                             for file in os.listdir(picturepath):
#                                 sstr1 = os.path.join('./media/himalaya/images/', subjecttype, file)
#                                 str1 = file.split('.')
#                                 if (str(str1[0]) == table.cell(i, 0).value):
#                                     flagp = 1
#                                     sourcecpy(os.path.join(picturepath, file), './media/himalaya/images/' + subjecttype)
#                                     fbi.picture = 'himalaya/images/' + subjecttype + '/' + file
#                                     fbi.save()
#                             if (flagp == 0):
#                                 errorpicture.append(fbi.filecode)
#                         for item in manytomany:
#                             mt = fbi._meta.get_field(item)
#                             m = mt.related_model
#                             itemstr = manytomany[item]
#                             mod = m.objects.all()
#                             manyflag = 0
#                             for v in mod:
#                                 if (str(v) == itemstr):
#                                     manyflag = 1
#                                     s = 'FileBaseInfo_' + item
#                                     modelnames = apps.get_app_config('himalaya').get_model(s)
#                                     try:
#                                         modelname = modelnames.objects.get(filebaseinfo_id=fbi.id)
#                                     except ObjectDoesNotExist:
#                                         modelnames = apps.get_app_config('himalaya').get_model(s)
#                                         modelname = modelnames()
#                                         setattr(modelname, "filebaseinfo_id", int(fbi.id))
#                                     setattr(modelname, m._meta.model_name + '_id', int(v.id))
#                                     modelname.save()
#                             if(manyflag==0):
#                                 manyerror[fbi.filecode] = itemstr
#                         if (dynamicfilebaseid != -1):
#                             for item in extend:
#                                 if(extend[item]!='') :
#                                     try:
#                                         fextend = FileExtendInfo.objects.get(fileId=fbi.id,fieldId=int(item))
#                                     except ObjectDoesNotExist:
#                                         fextend = FileExtendInfo()
#                                         fextend.fileId = fbi.id
#                                         fextend.fieldId = int(item)
#                                     if (int(SubjectTheme.objects.get(id=int(item)).fieldType) == 6 or int(
#                                             SubjectTheme.objects.get(id=int(item)).fieldType) == 5):
#                                         pid = SubjectTheme.objects.get(id=int(item)).corrAttri
#                                         global featureid
#                                         featureid = None
#                                         checktrees(int(pid),str(extend[item]).strip())
#                                         if featureid!=None:
#                                             fextend.filedValue = featureid
#                                             fextend.save()
#                                         else:
#                                             extenderror[fbi.filecode]=extend[item]
#                                     else:
#                                         fextend.filedValue = extend[item]
#                                         fextend.save()
#                         print table.cell(i, 0).value, 'success'
#                     except ObjectDoesNotExist:
#                         repetition.append(str(table.cell(i, 0).value))
#         if(attachpath!=-1 and attachpath!=-2):
#             shutil.rmtree(attachpath)
#         if(picturepath!=-1 and picturepath!=-2):
#             shutil.rmtree(picturepath)
#         if(len(repetition)!=0 or len(errorfile)!=0 or len(extenderror)!=0 or len(manyerror)!=0 or len(errorpicture)!=0) or attachpath==-2 or picturepath==-2:
#             request.session['repetiton'] = repetition
#             request.session['errorfile'] = errorfile
#             request.session['errorpicture'] = errorpicture
#             request.session['extenderror'] = extenderror
#             request.session['manyerror'] = manyerror
#             request.session['attachpath'] = attachpath2
#             request.session['picturepath'] = imagepath1
#             return redirect('/xadmin/himalaya/modifyaddr/')
#
#         else:
#             print 'guokena'
#             return redirect("../")
#     else:
#         form = swfForm()
#     return render_to_response("xadmin/himalaya/filebaseinfo/swfmodify.html", {"form": form})

def modifyaddr(request):
    repetition =  request.session.get('repetiton')
    errorfile =  request.session.get('errorfile')
    errorpicture = request.session.get('errorpicture')
    extenderror= request.session.get('extenderror')
    manyerror = request.session.get('manyerror')
    attachpath = request.session.get('attachpath')
    picturepath = request.session.get('picturepath')
    print repetition, len(repetition)
    print errorfile, len(errorfile)
    print extenderror, len(extenderror)
    print manyerror, len(manyerror)
    print errorpicture, len(errorpicture)
    print attachpath,picturepath
    if (request.method == "POST"):
        return redirect('/xadmin/himalaya/filebaseinfo/')
    return render_to_response("xadmin/himalaya/filebaseinfo/modifyaddr.html",{"repetition":repetition,"errorfile":errorfile,"extenderror":extenderror,"manyerror":manyerror,"errorpicture":errorpicture,
                                                   "attachpath":attachpath,"picturepath":picturepath})

def checktrees(id,name):
    item = Category.objects.get(id=id)
    if(item.attrName==name):
        global featureid
        featureid = item.id
        return featureid
    else:
        item = Category.objects.filter(pid=id)
        for num in item:
            checktrees(num.id,name)

def GetFileNameAndExt(filename):
    filepath,tempfilename = os.path.split(filename)
    shotname,extension = os.path.splitext(tempfilename)
    return shotname,extension

def sourcecpy(src, des):
    src = os.path.normpath(src)
    des = os.path.normpath(des)
    if not os.path.exists(src) or not os.path.exists(des):
        print("文件路径不存在")
        sys.exit(1)
    # for file in os.listdir(src):
    #     src_file = os.path.join(src, file)
    #     shutil.copy(src_file,des)
    shutil.copy(src,des)

# def swfchoice(request):
#     path = request.session.get('path')
#     dynamicfilebaseid = request.session.get('dynamicfilebaseid')
#     ss = xlrd.open_workbook(path)
#     table = ss.sheets()[0]
#     data = table.row_values(0)
#     fields = FileBaseInfo._meta.get_fields()
#     many = FileBaseInfo._meta.many_to_many
#     value = [('-1','---------')]
#     flage = {}
#     flage['-1'] = -1
#     for field in fields:
#         if (field.name != 'subjecttype' and field.name != 'id' and field.name != 'uploadDate' and field.name != 'updateDate' and field.name !='size' and field.name!='contentLength'):
#                 flage[field.name] = 0
#                 value.append((field.name,field.verbose_name))
#     for field in many:
#         flage[field.name] = 2
#         value.append((field.name,field.verbose_name))
#     dynamicfilebaseid = int(dynamicfilebaseid)
#     if (dynamicfilebaseid == -1):
#         pass
#     else:
#         extend = SubjectTheme.objects.filter(subjectId=dynamicfilebaseid)
#         for field in extend:
#             value.append((field.id, field.fieldName))
#             flage[str(field.id)] = 1
#     class swfForm(forms.Form):
#             eenumnames = locals()
#             eenum = len(data)
#             for i in range(len(data)):
#                 eenumnames['data%s' % i] = forms.ChoiceField(label=data[i],
#                                                               choices=value)
#             i = len(data)
#             eenumnames["data%s" % i] = forms.FileField(label=u'缩略图')
#             i = i + 1
#             eenumnames["data%s" % i] = forms.FileField(label=u'附件')
#     if request.method =='POST':
#         form = swfForm(request.POST, request.FILES)
#         dict = []
#         if(dynamicfilebaseid!=-1 and dynamicfilebaseid!=0):
#             subject = Subject.objects.get(id=int(dynamicfilebaseid))
#             subjecttype = subject.subjectName
#             spath = os.path.normpath('./media/himalaya/files/'+subjecttype)
#             if not os.path.exists(spath) or not os.path.isdir(spath):
#                 os.mkdir('./media/himalaya/files/'+subjecttype)
#             spath =  os.path.normpath('./media/himalaya/images/'+subjecttype)
#             if not os.path.exists(spath) or not os.path.isdir(spath):
#                 os.mkdir('./media/himalaya/images/'+subjecttype)
#         s = request.FILES.get('data%s' % len(data))
#         picturepath = -1
#         attachpath = -1
#         imagepath1 = -1
#         attachpath2 = -1
#         errorfile =[]
#         errorpicture =[]
#         if s:
#             st = s.name
#             imagepath = default_storage.save('himalaya/images/'+str(st), ContentFile(s.read()))
#             # if(GetFileNameAndExt(imagepath)=='rar'):
#             #     # file = rarfile.RarFile(imagepath)  # 这里写入的是需要解压的文件，别忘了加路径
#             #     # file.extractall('./media/himalaya/images/'+subjecttype)
#             # if (GetFileNameAndExt(imagepath) == 'zip'):
#             if(os.path.isfile('./media/'+imagepath)):
#                 f = zipfile.ZipFile('./media/'+imagepath, 'r')
#                 if(f.testzip()==None):
#                     for file in f.namelist():
#                         f.extract(file, './media/himalaya/images/')
#                     picturepath = './media/himalaya/images/'+f.namelist()[0]
#                 else:
#                     picturepath = -2
#                     imagepath1 = st
#                 os.remove('./media/' + imagepath)
#             else:
#                 print 'not found'
#         s = request.FILES.get('data%s' % (len(data) + 1))
#         if s:
#             st = s.name
#             attachpath1 = default_storage.save('./himalaya/files/' + str(st), ContentFile(s.read()))
#             # if (GetFileNameAndExt(attachpath) == 'rar'):
#             #     file = rarfile.RarFile(attachpath)  # 这里写入的是需要解压的文件，别忘了加路径
#             #     file.extractall('./media/himalaya/files/' + subjecttype)
#             # if (GetFileNameAndExt(attachpath) == 'zip'):
#             if(os.path.isfile('./media/'+attachpath1)):
#                 f = zipfile.ZipFile('./media/'+attachpath1, 'r')
#                 print f.testzip()
#                 if(f.testzip()==None):
#                     for file in f.namelist():
#                         f.extract(file, './media/himalaya/files/')
#                     attachpath = './media/himalaya/files/'+f.namelist()[0]
#                 else:
#                     attachpath =  -2
#                     attachpath2 = st
#                 os.remove('./media/' + attachpath1)
#             else:
#                 print 'not found'
#         repetition = []
#         extenderror = {}
#         manyerror = {}
#         if(attachpath!=-2 and picturepath!=-2):
#             for i in range(len(data)):
#                 s = form['data%s' % i].value()
#                 dict.append(s)
#             nrows = table.nrows
#             for i in range(1, nrows):
#                 if(table.cell(i, 0).value):
#                     try:
#                         FileBaseInfo.objects.get(filecode=table.cell(i, 0).value)
#                         repetition.append(str(table.cell(i, 0).value))
#                     except ObjectDoesNotExist:
#                         fbi = FileBaseInfo()
#                         extend = {}
#                         manytomany = {}
#                         fbi.uploadPeople = 'admin'
#                         for j in range(len(data)):
#                             s = dict[j]
#                             if table.cell(i, j).value:
#                                 if (int(flage[s]) == 0):
#                                     # mt = fbi._meta.get_field(s)
#                                     if (type(fbi._meta.get_field(s)) == django.db.models.fields.DateField):
#                                         date = table.cell(i, j).value
#                                         m = date.decode('utf-8').split(u"年".decode('utf-8'))
#                                         year = m[0]
#                                         if (len(m) > 1 and u"月".decode('utf-8') in m[1]):
#                                             m = m[1].split(u"月".decode('utf-8'))
#                                             month = m[0]
#                                             if (len(m) > 1 and u"日".decode('utf-8') in m[1]):
#                                                 m = m[1].split(u"日".decode('utf-8'))
#                                                 day = m[0]
#                                             else:
#                                                 day = '01'
#                                         else:
#                                             month = '01'
#                                             day = '01'
#                                         date = str(year) + str(month) + str(day)
#                                         date = datetime.strptime(''.join(date), "%Y%m%d").date()
#                                         setattr(fbi, s, date)
#                                     else:
#                                         setattr(fbi, s, table.cell(i, j).value)
#                                 elif (int(flage[s]) == 1):
#                                     extend[s] = table.cell(i, j).value
#                                 elif (int(flage[s]) == 2):
#                                     manytomany[s] = table.cell(i, j).value
#                         setattr(fbi, 'subjecttype', dynamicfilebaseid)
#                         flagp=0
#                         if(attachpath!=-1):
#                             for file in os.listdir(attachpath):
#                                 sstr1 = os.path.join('./media/himalaya/files/', subjecttype, file)
#                                 str1 = file.split('.')
#                                 if(str(str1[0])==table.cell(i,0).value):
#                                     flagp=1
#                                     sourcecpy(os.path.join(attachpath,file), './media/himalaya/files/' + subjecttype)
#                                     fbi.attachment='himalaya/files/' +subjecttype+'/'+file
#                                     fbi.size = os.path.getsize(sstr1)
#                                     if(str1[1]=='pdf'):
#                                         pdf = PdfFileReader(open(sstr1, "r"))
#                                         fbi.contentLength = pdf.getNumPages()
#                             if(flagp==0):
#                                 errorfile.append(fbi.filecode)
#                         flagp = 0
#                         if(picturepath!=-1):
#                             for file in os.listdir(picturepath):
#                                 sstr1 = os.path.join('./media/himalaya/images/', subjecttype, file)
#                                 str1 = file.split('.')
#                                 if (str(str1[0]) == table.cell(i, 0).value):
#                                     flagp = 1
#                                     sourcecpy(os.path.join(picturepath,file), './media/himalaya/images/' + subjecttype)
#                                     fbi.picture = 'himalaya/images/' + subjecttype + '/' + file
#                             if(flagp==0):
#                                 errorpicture.append(fbi.filecode)
#                         fbi.save()
#                         st = FileBaseInfo.objects.get(id=fbi.id)
#                         for item in manytomany:
#                             mt = st._meta.get_field(item)
#                             m = mt.related_model
#                             itemstr = manytomany[item]
#                             mod = m.objects.all()
#                             manyflag=0
#                             for v in mod:
#                                 if (str(v) == itemstr):
#                                     manyflag=1
#                                     s = 'FileBaseInfo_' + item
#                                     modelnames = apps.get_app_config('himalaya').get_model(s)
#                                     modelname = modelnames()
#                                     setattr(modelname, "filebaseinfo_id", int(st.id))
#                                     setattr(modelname, m._meta.model_name + '_id', int(v.id))
#                                     modelname.save()
#                             if(manyflag==0):
#                                 manyerror[fbi.filecode]=itemstr
#                         if (dynamicfilebaseid != -1):
#                             for item in extend:
#                                 fextend = FileExtendInfo()
#                                 fextend.fileId = fbi.id
#                                 fextend.fieldId = int(item)
#                                 if (int(SubjectTheme.objects.get(id=int(item)).fieldType) == 6 or int(
#                                         SubjectTheme.objects.get(id=int(item)).fieldType) == 5):
#                                     pid = SubjectTheme.objects.get(id=int(item)).corrAttri
#                                     global featureid
#                                     featureid = None
#                                     checktrees(int(pid), extend[item])
#                                     if featureid!=None:
#                                         fextend.filedValue = featureid
#                                     else:
#                                         extenderror[fbi.filecode]=extend[item]
#                                         fextend.filedValue = 'NULL'
#                                 else:
#                                     fextend.filedValue = extend[item]
#                                 fextend.save()
#                         print table.cell(i, 0).value, 'success'
#         if(attachpath!=-1 and attachpath!=-2):
#             shutil.rmtree(attachpath)
#         if(picturepath!=-1 and picturepath!=-2):
#             shutil.rmtree(picturepath)
#         print repetition
#         if(len(repetition)!=0 or len(errorfile)!=0 or len(extenderror)!=0 or len(manyerror)!=0 or len(errorpicture)!=0) or attachpath==-2 or picturepath==-2:
#             request.session['repetiton'] = repetition
#             request.session['errorfile'] = errorfile
#             request.session['errorpicture'] = errorpicture
#             request.session['extenderror'] = extenderror
#             request.session['manyerror'] = manyerror
#             request.session['attachpath'] = attachpath2
#             request.session['picturepath'] = imagepath1
#             return redirect('/xadmin/himalaya/swfaddr/')
#         else:
#             return redirect('../')
#     else:
#         form = swfForm()
#     return render_to_response("xadmin/himalaya/filebaseinfo/swfchoice.html",{"form": form})
# # return render_to_response("xadmin/himalaya/filebaseinfo/swfchoice.html",{"form":form,"flage":json.dumps(flage),"path":path,"dynamic":dynamicfilebaseid})
#
def swfaddr(request):

    repetition =  request.session.get('repetiton')
    errorfile =  request.session.get('errorfile')
    errorpicture = request.session.get('errorpicture')
    extenderror= request.session.get('extenderror')
    manyerror = request.session.get('manyerror')
    attachpath = request.session.get('attachpath')
    picturepath = request.session.get('picturepath')
    formaterror = request.session.get('formaterror')
    print repetition, len(repetition)
    print formaterror,len(formaterror)
    print errorfile, len(errorfile)
    print extenderror, len(extenderror)
    print manyerror, len(manyerror)
    print errorpicture, len(errorpicture)
    print attachpath,picturepath
    if(request.method=="POST"):
        return redirect("/xadmin/himalaya/filebaseinfo/")
    return render_to_response("xadmin/himalaya/filebaseinfo/swfaddr.html",
                              {"repetition": repetition, "errorfile": errorfile, "extenderror": extenderror,
                               "manyerror": manyerror, "errorpicture": errorpicture,
                               "attachpath": attachpath, "picturepath": picturepath,"formaterror":formaterror})

#     if request.method == 'POST':
#         form = swfForm(request.POST,request.FILES)
#         form = request.POST.get('data')
#         path = request.POST.get('path')
#         dynamicfilebaseid = request.POST.get('dynamic')
#         flage = request.POST.get('flage')
#         flage = json.loads(flage)
#         ss = xlrd.open_workbook(str(path))
#         table = ss.sheets()[0]
#         data = table.row_values(0)
#         dict = []
#         form = form.decode('utf-8')
#         form = json.loads(form)
#         subject = Subject.objects.get(id=str(dynamicfilebaseid))
#         subjecttype = subject.subjectName
#         s = request.FILES.get('data%s' % len(data))
#         st = s.name
#         imagepath = default_storage.save('./himalaya/images/' + st, ContentFile(s.read()))
#         imagepath = './media/himalaya/images/' + str(st)
#         unzip_file(imagepath,'./media/himalaya/images/'+subjecttype)
#         s = request.FILES.get('data%s' % (len(data)+1))
#         st = s.name
#         attachpath = default_storage.save('./himalaya/files/'+st, ContentFile(s.read()))
#         attachpath = './media/himalaya/files/' + str(st)
#         unzip_file(imagepath, './media/himalaya/files/'+subjecttype)
#         for i in range(len(data)):
#             s = form['data%s' % i]
#             dict.append(s)
#         nrows = table.nrows
#         repetition = []
#         for i in range(1,nrows):
#             try:
#                 FileBaseInfo.objects.get(filecode=table.cell(i, 0).value)
#                 repetition.append(table.cell(i, 0))
#             except ObjectDoesNotExist:
#                 fbi = FileBaseInfo()
#                 extend = {}
#                 manytomany = {}
#                 for j in range(len(data)):
#                     s = dict[j]
#                     if table.cell(i, j).value:
#                         if(int(flage[s])==0):
#                                 #mt = fbi._meta.get_field(s)
#                             if(type(fbi._meta.get_field(s))==django.db.models.fields.DateField):
#                                 date = table.cell(i, j).value
#                                 m = date.decode('utf-8').split(u"年".decode('utf-8'))
#                                 year = m[0]
#                                 if(len(m)>1 and u"月".decode('utf-8') in m[1]):
#                                     m = m[1].split(u"月".decode('utf-8'))
#                                     month = m[0]
#                                     if(len(m)>1 and u"日".decode('utf-8') in m[1]):
#                                         m = m[1].split(u"日".decode('utf-8'))
#                                         day = m[0]
#                                     else:
#                                         day = '01'
#                                 else:
#                                     month = '01'
#                                     day = '01'
#                                 date = str(year)+str(month) +str(day)
#                                 date = datetime.strptime(''.join(date), "%Y%m%d").date()
#                                 setattr(fbi,s,date)
#                             else:
#                                 setattr(fbi,s,table.cell(i, j).value)
#                         elif(int(flage[s])==1):
#                             extend[s] = table.cell(i, j).value
#                         elif(int(flage[s])==2):
#                             manytomany[s] = table.cell(i,j).value
#                 setattr(fbi,'subjecttype',dynamicfilebaseid)
#                 fbi.save()
#                 st = FileBaseInfo.objects.get(id = fbi.id)
#                 for item in manytomany:
#                     mt = st._meta.get_field(item)
#                     m = mt.related_model
#                     itemstr = manytomany[item]
#                     mod = m.objects.all()
#                     for v in mod:
#                         if(str(v)==itemstr):
#                             s = 'FileBaseInfo_'+item
#                             modelnames = apps.get_app_config('himalaya').get_model(s)
#                             modelname = modelnames()
#                             setattr(modelname,"filebaseinfo_id",int(st.id))
#                             setattr(modelname,m._meta.model_name+'_id',int(v.id))
#                             modelname.save()
#                 if (dynamicfilebaseid != -1):
#                     for item in extend:
#                         fextend = FileExtendInfo()
#                         fextend.fileId = fbi.id
#                         fextend.fieldId = int(item)
#                         if(int(SubjectTheme.objects.get(id=int(item)).fieldType)==6 or int(SubjectTheme.objects.get(id=int(item)).fieldType)==5):
#                             pid = SubjectTheme.objects.get(id = int(item)).corrAttri
#                             global featureid
#                             checktrees(int(pid), extend[item])
#                             fextend.filedValue = featureid
#                         else:
#                             fextend.filedValue = extend[item]
#                         fextend.save()
#             percent = float(i/nrows)
#             print percent
#             request.session['percent'] = percent
#         return redirect("../")

def swfchoice(request):
    path = request.session.get('path')
    dynamicfilebaseid = request.session.get('dynamicfilebaseid')
    ss = xlrd.open_workbook(path)
    index = ss.nsheets
    table = ss.sheet_by_index(0)
    for i in range(index):
        if(ss.sheet_by_index(i).nrows!=0):
            table = ss.sheets()[i]
            break
    data = table.row_values(0)
    fields = FileBaseInfo._meta.get_fields()
    value = [('', '---------')]
    basic = []
    extend = []
    for i in range(0,len(data)):
        value.append((i,data[i]))
    for field in fields:
        if (field.name != 'subjecttype' and field.name != 'id' and field.name != 'uploadDate' and field.name != 'updateDate' and field.name != 'size' and field.name != 'contentLength' and field.name!='picture' and field.name != 'attachment'):
            basic.append(field.verbose_name)
    dynamicfilebaseid = int(dynamicfilebaseid)
    if (dynamicfilebaseid == 0):
        pass
    else:
        feature = SubjectTheme.objects.filter(subjectId=dynamicfilebaseid)
        for field in feature:
            extend.append((field.id,field.fieldName))
    class basicForm(forms.Form):
        eenumnames = locals()
        for i in range(len(basic)):
            eenumnames['basic%s' % i] = forms.ChoiceField(label=basic[i],
                                                              choices=value,required=False)
        i = len(basic)
        eenumnames["basic%s" % i] = forms.FileField(label=u'缩略图',required=False,widget=TextInput(attrs={'type':'file','multiple':'multiple', 'webkitdirectory':'webkitdirectory'}),
                                                    help_text=u'请上传缩略图!')
        i = i + 1
        eenumnames["basic%s" % i] = forms.FileField(label=u'附件', required=False,widget=TextInput(attrs={'type':'file','multiple':'multiple','webkitdirectory':'webkitdirectory'}),
                                                    error_messages={'required':u'请上传附件!'},help_text=u'请上传附件!')
    class extendForm(forms.Form):
        extends =locals()
        for i in range(len(extend)):
            extends['extend%s' % i] = forms.ChoiceField(label=extend[i][1],
                                                          choices=value,required=False)
    if request.method =='POST':
        basicform = basicForm(request.POST, request.FILES)
        extendform = extendForm(request.POST)
        if basicform.is_valid() and extendform.is_valid():
            rangeLetter = ('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
            dict = []
            dict1 = []
            subjecttype = ''
            if(dynamicfilebaseid!=0):
                subject = Subject.objects.get(id=int(dynamicfilebaseid))
                subjecttype = subject.subjectName
                spath = os.path.normpath('./media/himalaya/files/'+subjecttype)
                if not os.path.exists(spath) or not os.path.isdir(spath):
                    os.mkdir('./media/himalaya/files/'+subjecttype)
                spath = os.path.normpath('./media/himalaya/images/'+subjecttype)
                if not os.path.exists(spath) or not os.path.isdir(spath):
                    os.mkdir('./media/himalaya/images/'+subjecttype)
            else:
                subjecttype = '基础文献'
                spath = os.path.normpath('./media/himalaya/files/基础文献')
                if not os.path.exists(spath) or not os.path.isdir(spath):
                    os.mkdir('./media/himalaya/files/基础文献')
                spath = os.path.normpath('./media/himalaya/images/基础文献')
                if not os.path.exists(spath) or not os.path.isdir(spath):
                    os.mkdir('./media/himalaya/images/基础文献')
            picturepath = -2
            attachpath = -2
            existimag = 1
            imagepath1 = ''
            attachpath2 = ''
            errorfile =[]
            errorpicture =[]
            newFileName = random.choice(rangeLetter) + random.choice(rangeLetter) + time.strftime('%M%S',
                                                                                                  time.localtime(
                                                                                                    time.time()))
            s = request.FILES.getlist('basic%s' % len(basic))
            if s:
                os.mkdir('./media/himalaya/images/'+newFileName)
                for file in s:
                    st = file.name
                    imagepath = default_storage.save('himalaya/images/'+newFileName+'/'+st, ContentFile(file.read()))
                    # print(os.path.abspath(imagepath))
                picturepath = 0
            else:
                existimag = 0
            s = request.FILES.getlist('basic%s' % (len(basic) + 1))
            if s:
                os.mkdir('./media/himalaya/files/'+newFileName)
                for file in s:
                    st = file.name
                    attachpath1 = default_storage.save('himalaya/files/'+newFileName+'/'+st, ContentFile(file.read()))
                attachpath = 0
            repetition = []
            extenderror = {}
            manyerror = {}
            formaterror={}
            if(attachpath!=-2 and (picturepath!=-2 or existimag==0)):
                for i in range(len(basic)):
                    s = basicform['basic%s' % i].value()
                    dict.append(s)
                for i in range(len(extend)):
                    s = extendform['extend%s' % i].value()
                    dict.append(s)
                nrows = table.nrows
                for i in range(1, nrows):
                    if(table.cell(i, 0).value):
                        try:
                            FileBaseInfo.objects.get(filecode=str(table.cell(i, 0).value).strip())
                            repetition.append(str(table.cell(i, 0).value).strip())
                        except ObjectDoesNotExist:
                            fbi = FileBaseInfo()
                            fbi.filecode = str(table.cell(i, 0).value)
                            #日期类型转换
                            date = None
                            p = u'[0-9]{4}年([0-9]{1,2}月)?([0-9]{1,2}日)?'
                            if dict[7]!='':
                                temstr = str(table.cell(i, int(dict[7])).value).strip()
                                temstr = temstr.decode('utf-8')
                                if re.search(p,temstr):
                                    date = temstr
                                    m = date.decode('utf-8').split(u"年".decode('utf-8'))
                                    year = m[0]
                                    if (len(m) > 1 and u"月".decode('utf-8') in m[1]):
                                        m = m[1].split(u"月".decode('utf-8'))
                                        month = m[0]
                                        if (len(m) > 1 and u"日".decode('utf-8') in m[1]):
                                            m = m[1].split(u"日".decode('utf-8'))
                                            day = m[0]
                                            date = str(year) + str(month) + str(day)
                                            date = datetime.strptime(''.join(date), "%Y%m%d").date()
                                        else:
                                            date = str(year) + str(month)
                                            date = datetime.strptime(''.join(date), "%Y%m").date()
                                    else:
                                        date = str(year)
                                        date = datetime.strptime(''.join(date), "%Y").date()
                                else:
                                    formaterror[str(table.cell(i, 0).value)] = temstr
                                    continue
                            # #图片匹配，文件匹配
                            # fileLength = None
                            # filesize = ''
                            # pic = 'himalaya/images'
                            # att = 'himalaya/files'
                            # if(existimag==1):
                            #     sstr1 = glob.glob(picturepath + str(table.cell(i, 0).value).strip() + '.*')
                            #     if len(sstr1)!=0:
                            #         pic = os.path.join('himalaya/images', subjecttype, os.path.basename(sstr1[0]))
                            #         if(os.path.exists(os.path.join('./media/himalaya/images', subjecttype, os.path.basename(sstr1[0])))):
                            #             os.remove(os.path.join('./media/himalaya/images', subjecttype, os.path.basename(sstr1[0])))
                            #         shutil.move(sstr1[0],'./media/himalaya/images/'+subjecttype)
                            #     else:
                            #         errorpicture.append(str(table.cell(i,0).value).strip())
                            #         continue
                            # sstr2 = glob.glob(attachpath+str(table.cell(i,0).value).strip()+'.*')
                            # if len(sstr2)!=0:
                            #     filesize = getsize(sstr2[0])
                            #     att = os.path.join('himalaya/files',subjecttype,os.path.basename(sstr2[0]))
                            #     filename = os.path.basename(sstr2[0])
                            #     str1 = filename.split('.')
                            #     if(str1[1]=='pdf'):
                            #         pdf = PdfFileReader(open(sstr2[0], "r"))
                            #         fileLength = pdf.getNumPages()
                            #         if (existimag == 0):
                            #             print('extract',str1[0])
                            #             pdf = Image(filename=sstr2[0])
                            #             print(pdf)
                            #             image = pdf.convert('jpg')
                            #             print(image)
                            #             image.save(filename='./media/himalaya/images/' + subjecttype + '/' +str1[0] + '.jpg')
                            #             # with Image(filename=sstr2[0]) as pdf:
                            #             #     with pdf.convert('jpg') as image:
                            #             #         image.save(filename='./media/himalaya/images/' + subjecttype + '/' +
                            #             #                      str1[0] + '.jpg')
                            #             pic = 'himalaya/images/' + subjecttype + '/' + str1[0] + '.jpg'
                            #     if(os.path.exists(os.path.join('./media/himalaya/files',subjecttype,os.path.basename(sstr2[0])))):
                            #         os.remove(os.path.join('./media/himalaya/files',subjecttype,os.path.basename(sstr2[0])))
                            #     shutil.move(sstr2[0],'./media/himalaya/files/'+subjecttype)
                            # else:
                            #     errorfile.append(str(table.cell(i,0).value).strip())
                            #     continue
                            # fbi.filecode=table.cell(i,0).value
                            # fbi.title=table.cell(i,int(dict[1])).value if dict[1] != '' else ''
                            # fbi.creator=table.cell(i,int(dict[2])).value if dict[2] != '' else ''
                            # fbi.keywords=table.cell(i,int(dict[3])).value if dict[3] != '' else ''
                            # fbi.description=table.cell(i,int(dict[4])).value if dict[4] != '' else ''
                            # fbi.publisher=table.cell(i,int(dict[5])).value if dict[5] != '' else ''
                            # fbi.contributor=table.cell(i,int(dict[6])).value if dict[6] != '' else ''
                            # fbi.pubDate=date
                            # fbi.uploadPeople=table.cell(i,int(dict[8])).value if dict[8]!='' else ''
                            # fbi.notes=table.cell(i,int(dict[9])).value if dict[9]!='' else ''
                            # fbi.check=False if dict[10] != '' and table.cell(i, int(dict[10])).value=='False' else True
                            # fbi.subjecttype=dynamicfilebaseid
                            # fbi.attachment=att
                            # fbi.picture=pic
                            # fbi.size=filesize
                            # fbi.contentLength=fileLength
                            flag = 0
                            filetype = []
                            lang = []
                            disc = []
                            spa = []
                            fileFor = []
                            querylist = {}
                            if dict[11] != '' and table.cell(i, int(dict[11])).value!='':
                                values = str(table.cell(i, int(dict[11])).value).decode('utf-8')
                                values = values.strip()
                                values = re.split(u';|；|,|，',values)
                                for item in values:
                                    try:
                                        # print (item)
                                        fileType = FileType.objects.get(fileTypeName=item.strip())
                                        filetype.append(fileType)
                                    except:
                                        manyerror[fbi.filecode]=item
                                        flag = 1
                                        break
                            if dict[12] != '' and table.cell(i,int(dict[12])).value!='' and flag==0:
                                values = str(table.cell(i,int(dict[12])).value).decode('utf-8')
                                values = values.strip()
                                values = re.split(u';|；|,|，', values)
                                for item in values:
                                    try:
                                        # print (item)
                                        language = Language.objects.get(lanTypeName=item.strip())
                                        lang.append(language)
                                    except:
                                        manyerror[fbi.filecode] = item
                                        flag = 1
                                        break
                            if dict[13] != '' and table.cell(i,int(dict[13])).value!='' and flag ==0:

                                values = str(table.cell(i,int(dict[13])).value).decode('utf-8')
                                values = values.strip()
                                values = re.split(u';|；|,|，', values)
                                for item in values:
                                    try:
                                        # print (item)
                                        discipline = Discipline.objects.get(disciplineTypeName=item.strip() )
                                        disc.append(discipline)
                                    except:
                                        manyerror[fbi.filecode] = item
                                        flag = 1
                                        break
                            if dict[14] != '' and table.cell(i,int(dict[14])).value!='' and flag == 0:

                                values = str(table.cell(i,int(dict[14])).value).decode('utf-8')
                                values = values.strip()
                                values = re.split(u';|；|,|，', values)
                                for item in values:
                                    try:
                                        # print (item)
                                        spatial = SpaceScope.objects.get(spcaeTypeName=item.strip())
                                        spa.append(spatial)
                                    except:
                                        manyerror[fbi.filecode] = item
                                        flag = 1
                                        break
                            if dict[15] != '' and table.cell(i,int(dict[15])).value!='' and flag ==0:
                                values = str(table.cell(i,int(dict[15])).value).decode('utf-8')
                                values = values.strip()
                                values = re.split(u';|；|,|，', values)
                                for item in values:
                                    try:
                                        # print (item)
                                        fileFormat = Format.objects.get(formatTypeName=item.strip())
                                        fileFor.append(fileFormat)
                                    except:
                                        manyerror[fbi.filecode] = item
                                        flag = 1
                                        break
                            if flag == 0:
                                for j in range(len(basic),len(basic)+len(extend)):
                                    if(dict[j]!='' and str(table.cell(i,int(dict[j])).value)!='' and flag==0):
                                        item = extend[j-len(basic)][0]
                                        fieldId = int(item)
                                        if (int(SubjectTheme.objects.get(id=int(item)).fieldType) == 6 or int(
                                                SubjectTheme.objects.get(id=int(item)).fieldType) == 5):
                                            values = str(table.cell(i, int(dict[j])).value).decode('utf-8')
                                            values = re.split(u',|，', values)
                                            fid = []
                                            for val in values:
                                                pid = SubjectTheme.objects.get(id=int(item)).corrAttri
                                                global featureid
                                                featureid = None
                                                checktrees(int(pid),val.strip())
                                                if featureid != None:
                                                    fid.append(featureid)
                                                else:
                                                    print (pid)
                                                    extenderror[fbi.filecode]=val
                                                    flag = 1
                                                    break
                                            querylist[item]=fid
                                        else:
                                            values = str(table.cell(i, int(dict[j])).value).decode('utf-8')
                                            values = values.strip()
                                            values = re.split(u',|，', values)
                                            fid = []
                                            for val in values:
                                                fid.append(val)
                                            querylist[item]=fid
                            if flag==0:
                                # 图片匹配，文件匹配
                                fileLength = None
                                filesize = ''
                                pic = 'himalaya/images'
                                att = 'himalaya/files'
                                sstr1 = ''
                                if (existimag == 1):
                                    sstr1 = glob.glob('./media/himalaya/images/'+newFileName+'/'+str(table.cell(i, 0).value).strip() + '.*')
                                    if len(sstr1) != 0:
                                        pic = os.path.join('himalaya/images', subjecttype, os.path.basename(sstr1[0]))
                                    else:
                                        errorpicture.append(str(table.cell(i, 0).value).strip())
                                        continue
                                sstr2 = glob.glob('./media/himalaya/files/'+newFileName+'/' + str(table.cell(i, 0).value).strip() + '.*')
                                if len(sstr2) != 0:
                                    filesize = getsize(sstr2[0])
                                    att = os.path.join('himalaya/files', subjecttype, os.path.basename(sstr2[0]))
                                    filename = os.path.basename(sstr2[0])
                                    str1 = filename.split('.')
                                    if (str1[1] == 'pdf'):
                                        try:
                                            pdf = PdfFileReader(open(sstr2[0], "r"))
                                            # fileLength = pdf.getNumPages()
                                            # if (existimag == 0):
                                            #     output = PdfFileWriter()
                                            #     output.addPage(pdf.getPage(0))
                                            #     outputStrem = open(
                                            #         './media/himalaya/images/' + subjecttype + '/' + str1[0] + '.pdf',
                                            #         'w')
                                            #     output.write(outputStrem)
                                            #     outputStrem.close()
                                            #     pic = 'himalaya/images/' + subjecttype + '/' + str1[0] + '.jpg'
                                            #     with Image(
                                            #             filename='./media/himalaya/images/' + subjecttype + '/' + str1[
                                            #                 0] + '.pdf') as pdf:
                                            #         with pdf.convert('jpg') as image:
                                            #             image.save(
                                            #                 filename='./media/himalaya/images/' + subjecttype + '/' +
                                            #                          str1[
                                            #                              0] + '.jpg')
                                            #     os.remove(
                                            #         './media/himalaya/images/' + subjecttype + '/' + str1[0] + '.pdf')
                                        except Exception:
                                            errorfile.append(str(table.cell(i, 0).value).strip())
                                            continue
                                        fileLength = pdf.getNumPages()
                                        if (existimag == 0):
                                            output = PdfFileWriter()
                                            output.addPage(pdf.getPage(0))
                                            outputStrem = open(
                                                './media/himalaya/images/' + subjecttype + '/' + str1[0] + '.pdf',
                                                'w')
                                            output.write(outputStrem)
                                            outputStrem.close()
                                            pic = 'himalaya/images/' + subjecttype + '/' + str1[0] + '.jpg'
                                            with Image(
                                                    filename='./media/himalaya/images/' + subjecttype + '/' + str1[
                                                        0] + '.pdf') as pdf:
                                                with pdf.convert('jpg') as image:
                                                    image.save(
                                                        filename='./media/himalaya/images/' + subjecttype + '/' +
                                                                 str1[
                                                                     0] + '.jpg')
                                            os.remove(
                                                './media/himalaya/images/' + subjecttype + '/' + str1[0] + '.pdf')
                                    if (os.path.exists(os.path.join('./media/himalaya/files', subjecttype,os.path.basename(sstr2[0])))):
                                        os.remove(os.path.join('./media/himalaya/files', subjecttype,os.path.basename(sstr2[0])))
                                    shutil.move(sstr2[0], './media/himalaya/files/' + subjecttype)
                                else:
                                    print ('visit',fbi.filecode)
                                    errorfile.append(str(table.cell(i, 0).value).strip())
                                    continue
                                if (existimag == 1):
                                    if (os.path.exists(os.path.join('./media/himalaya/images', subjecttype,
                                                                    os.path.basename(sstr1[0])))):
                                        os.remove(os.path.join('./media/himalaya/images', subjecttype,
                                                               os.path.basename(sstr1[0])))
                                    shutil.move(sstr1[0], './media/himalaya/images/' + subjecttype)
                                fbi.filecode = str(table.cell(i, 0).value).strip()
                                fbi.title = str(table.cell(i, int(dict[1])).value).strip() if dict[1] != '' else ''
                                fbi.creator = str(table.cell(i, int(dict[2])).value).strip() if dict[2] != '' else ''
                                fbi.keywords = str(table.cell(i, int(dict[3])).value).strip() if dict[3] != '' else ''
                                fbi.description = str(table.cell(i, int(dict[4])).value).strip() if dict[4] != '' else ''
                                fbi.publisher = str(table.cell(i, int(dict[5])).value).strip() if dict[5] != '' else ''
                                fbi.contributor = str(table.cell(i, int(dict[6])).value).strip() if dict[6] != '' else ''
                                fbi.pubDate = date
                                fbi.uploadPeople = str(table.cell(i, int(dict[8])).value).strip() if dict[8] != '' else ''
                                fbi.notes = str(table.cell(i, int(dict[9])).value).strip() if dict[9] != '' else ''
                                fbi.check = False if dict[10] != '' and str(table.cell(i, int(
                                    dict[10])).value).strip() == 'False' else True
                                fbi.subjecttype = dynamicfilebaseid if dynamicfilebaseid!=0 else -1
                                fbi.attachment = att
                                fbi.picture = pic
                                fbi.size = filesize
                                fbi.contentLength = fileLength
                                fbi.save()
                                if(len(filetype)!=0):
                                    for item in filetype:
                                        fbi.fileType.add(item)
                                if(len(lang)!=0):
                                    for item in lang:
                                        fbi.language.add(item)
                                if(len(disc)!=0):
                                    for item in disc:
                                        fbi.discipline.add(disc)
                                if(len(spa)!=0):
                                    for item in spa:
                                        fbi.spatial.add(item)
                                if(len(fileFor)!=0):
                                    for item in fileFor:
                                        fbi.fileFormat.add(item)
                                fbi.save()
                                query = []
                                for key,temval in querylist.items():
                                    for value in temval:
                                        query.append(FileExtendInfo(fileId=fbi.id,fieldId=key,filedValue=value))
                                if(len(query)!=0):
                                    FileExtendInfo.objects.bulk_create(query)
                                print(fbi.filecode,'success')
            if(attachpath!=-2):
                shutil.rmtree('./media/himalaya/files/'+newFileName)
            if(picturepath!=-2):
                shutil.rmtree('./media/himalaya/images/'+newFileName)
            if(len(repetition)!=0 or len(errorfile)!=0 or len(extenderror)!=0 or len(manyerror)!=0 or len(errorpicture)!=0) or attachpath==-2 or picturepath==-2 or len(formaterror)!=0:
                request.session['repetiton'] = repetition
                request.session['errorfile'] = errorfile
                request.session['errorpicture'] = errorpicture
                request.session['extenderror'] = extenderror
                request.session['manyerror'] = manyerror
                request.session['attachpath'] = attachpath2
                request.session['picturepath'] = imagepath1
                request.session['formaterror'] = formaterror
                return redirect('/xadmin/himalaya/swfaddr/')
            else:
                messages.info(request,'文献保存成功!')
                return redirect('../',{})
    else:
        basicform = basicForm()
        extendform = extendForm()
    return render_to_response("xadmin/himalaya/filebaseinfo/swfchoice.html",{"basicform": basicForm,"extendform":extendform})
# return render_to_response("xadmin/himalaya/filebaseinfo/swfchoice.html",{"form":form,"flage":json.dumps(flage),"path":path,"dynamic":dynamicfilebaseid})

def getdata(it,i):
    global level
    if(level<i): level = i
    tmp = Category.objects.filter(pid = int(it.id))
    lis = []
    for item in tmp:
        data = dict()
        data['name'] = item.attrName
        data['value'] = item.id
        if( Category.objects.filter(pid = int(item.id))):
            data['sub'] = getdata(item,i+1)
        lis.append(data)
    return lis
# 修改图片地址
def test(request):
    return render_to_response('xadmin/himalaya/test.html',{})


class TestOnlySignalProcessor(signals.BaseSignalProcessor):
    def setup(self):
        # Listen only to the ``User`` model.
        models.signals.post_save.connect(self.handle_save, sender=User)
        models.signals.post_delete.connect(self.handle_delete, sender=User)

    def teardown(self):
        # Disconnect only for the ``User`` model.
        models.signals.post_save.disconnect(self.handle_save, sender=User)
        models.signals.post_delete.disconnect(self.handle_delete, sender=User)





# 实现按字母排序函数定义的开始------------------------------------------
# 建立拼音辞典
dic_py = dict()
f_py = open('py.txt', "r")
content_py = f_py.read()
lines_py = content_py.split('\n')
n = len(lines_py)
for i in range(0, n - 1):
    word_py, mean_py = lines_py[i].split('\t', 1)  # 将line用\t进行分割，最多分一次变成两块，保存到word和mean中去
    dic_py[word_py] = mean_py
f_py.close()

# 建立笔画辞典
dic_bh = dict()
f_bh = open('bh.txt', "r")
content_bh = f_bh.read()
lines_bh = content_bh.split('\n')
n = len(lines_bh)
for i in range(0, n - 1):
    word_bh, mean_bh = lines_bh[i].split('\t', 1)  # 将line用\t进行分割，最多分一次变成两块，保存到word和mean中去
    dic_bh[word_bh] = mean_bh
f_bh.close()


# 辞典查找函数
def searchdict(dic, uchar):
    if isinstance(uchar, str):
        uchar = unicode(uchar, 'utf-8')
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        value = dic.get(uchar.encode('utf-8'))
        if value == None:
            value = '*'
    else:
        value = uchar
    return value


# 比较单个字符
def comp_char_PY(A, B):
    if A == B:
        return -1
    pyA = searchdict(dic_py, A)
    pyB = searchdict(dic_py, B)
    if pyA > pyB:
        return 1
    elif pyA < pyB:
        return 0
    else:
        bhA = eval(searchdict(dic_bh, A))
        bhB = eval(searchdict(dic_bh, B))
        if bhA > bhB:
            return 1
        elif bhA < bhB:
            return 0
        else:
            return "Are you kidding?"


# 比较字符串
def comp_char(A, B):
    charA = A.decode("utf-8")
    charB = B.decode("utf-8")
    n = min(len(charA), len(charB))
    i = 0
    while i < n:
        dd = comp_char_PY(charA[i], charB[i])
        if dd == -1:
            i = i + 1
            if i == n:
                dd = len(charA) > len(charB)
        else:
            break
    return dd


# 排序函数
def cnsort(nline):
    n = len(nline)
    for i in range(1, n):  # 插入法
        tmp = nline[i]
        j = i
        while j > 0 and comp_char(nline[j-1],tmp):
            nline[j] = nline[j-1]
            j -= 1
        nline[j] = tmp
    return nline

def cnsortlist(nlist):
    n = len(nlist)
    for i in range(1,n):
        tmp = nlist[i]
        j = i
        print nlist[j-1][1]
        while j > 0 and comp_char(nlist[j-1][1],tmp[1]):
            nlist[j] = nlist[j-1]
            j -= 1
        nlist[j]=tmp
    return nlist

# 实现按字母排序函数的结束------------------------------------------

def Routeadd(req):
    if(req.method=='POST'):
        form = RouteForm(req.POST)
        item = Route()
        item.bookID_id = form['bookID'].value()
        item.RouteName = form['RouteName'].value()
        if form['RoutePer'].value():
            item.RoutePer = form['RoutePer'].value()
        if form['remark'].value():
            item.remark = form['remark'].value()
        item.save()
        return redirect('..', {})
    else:
        form = RouteForm()
        ftchoice=OrderedDict()
        data = BookList.objects.all()
        bookdetail=[]
        for item in data:
            ftchoice[item.bookID] = item.bNameCH +'/' +item.author
            bookdetail.append([str(item.bookID),str(item.bNameCH),str(item.author),str(item.press),item.pubdate,item.pageNum])

        # ------------------------------------------------------------实现按字母排序
        newftchoice = dict()
        for key, value in ftchoice.items():
            newftchoice[value] = key
        newftchoice = [(k, newftchoice[k]) for k in cnsort(newftchoice.keys())]
        ftchoice.clear()
        for key in newftchoice:
            ftchoice[key[1]] = key[0]
        # ----------------------------------------------------------实现按字母排序结束

        return render_to_response('xadmin/himalaya/route/add.html', {'form': form, 'ftchoice': ftchoice,'bookdetail':bookdetail})


def Routeupdate(req,id):
    item = Route.objects.get(id=int(id))
    if(req.method=='POST'):
        form = RouteForm(req.POST)
        item.bookID_id = form['bookID'].value()
        item.RouteName = form['RouteName'].value()
        if form['RoutePer'].value():
            item.RoutePer = form['RoutePer'].value()
        if form['remark'].value():
            item.remark = form['remark'].value()
        item.save()
        return redirect('../..', {})
    else:
        ftchoice=OrderedDict()
        data = BookList.objects.all()
        bookdetail=[]
        items=BookList.objects.get(bookID=item.bookID)
        for tmp in data:
            ftchoice[tmp.bookID] = tmp.bNameCH +'/' +tmp.author
            bookdetail.append([str(tmp.bookID), str(tmp.bNameCH), str(tmp.author), str(tmp.press),str(tmp.pubdate), str(tmp.pageNum)])

        # ------------------------------------------------------------实现按字母排序
        newftchoice = dict()
        for key, value in ftchoice.items():
            newftchoice[value] = key
        newftchoice = [(k, newftchoice[k]) for k in cnsort(newftchoice.keys())]
        ftchoice.clear()
        for key in newftchoice:
            ftchoice[key[1]] = key[0]
            # ----------------------------------------------------------实现按字母排序结束

        return render_to_response('xadmin/himalaya/route/update.html', {'form': item, 'ftchoice': ftchoice,'bookID':str(item.bookID),'bookdetail':bookdetail,'bookname':str(items.bNameCH),
                                                                        'author':str(items.author),'press':str(items.press),'pubdate':str(items.pubdate),'pagenum':str(items.pageNum)})


def traveladd(req):
    if(req.method=='POST'):
        routename = req.GET['_rel_RouteName__id__exact']
        form = traveldata_form(req.POST,req.FILES)
        item = TravelData()
        toa = str(form['toa'].value()).split('/')
        item.toa = datetime.strptime(''.join(toa), "%Y%m%d").date()
        tol = str(form['tol'].value()).split('/')
        item.tol = datetime.strptime(''.join(tol), "%Y%m%d").date()
        item.agriculture = form['agriculture'].value()
        item.economy=form['economy'].value()
        item.custom = form['custom'].value()
        item.education = form['education'].value()
        item.geography = form['geography'].value()
        item.siteid_id = form['siteid'].value()
        item.DataPage = form['DataPage'].value()
        item.nation = form['nation'].value()
        item.transportation = form['transportation'].value()
        item.police = form['police'].value()
        item.other = form['other'].value()
        item.religion = form['religion'].value()
        item.history = form['history'].value()
        item.inputUser = form['inputUser'].value()
        item.RouteName_id = routename
        item.mileage = form['mileage'].value()
        result = TravelData.objects.filter(RouteName_id = int(routename))
        item.order = len(result)
        item.save()
        s = req.FILES.getlist('picture')
        if s:
            for file in s:
                st = file.name
                imagepath = default_storage.save('himalaya/travelgraph/' + st, ContentFile(file.read()))
                pic = Travelgraph()
                pic.graph = 'himalaya/travelgraph/' + st
                pic.traverData_id = item.id
                pic.save()
        return  redirect('../?_rel_RouteName__id__exact='+str(routename))
    else:
        with open('creatree.pkl', 'rb') as file:
            ass = cPickle.load(file)
            file.close()
        data = ass[0]
        levelist = ass[1]
        addre = OrderedDict()
        for item in Site.objects.all():
            reg = item.region
            while (reg.id != 273):
                if str(reg.id) not in addre:
                    addre[str(reg.id)] = [(item.id, item.sitenameCH)]
                else:
                    addre[str(reg.id)].append((item.id, item.sitenameCH))
                reg = reg.pid

        # ------------------------------------------------------------实现按字母排序
        for key,value in addre.items():
            addre[key]=cnsortlist(value)

        # ----------------------------------------------------------实现按字母排序结束

        return render_to_response('xadmin/himalaya/traveldata/add.html',{'data': json.dumps(data), 'level': levelist,
                                                                    'context_instance': RequestContext(req),'addre':json.dumps(addre)})

def travelupdate(req,id):
    if (req.method == 'POST'):
        form = traveldata_form(req.POST, req.FILES)
        item = TravelData.objects.get(id=int(id))
        toa = str(form['toa'].value()).split('/')
        item.toa = datetime.strptime(''.join(toa), "%Y%m%d").date()
        tol = str(form['tol'].value()).split('/')
        item.tol = datetime.strptime(''.join(tol), "%Y%m%d").date()
        item.agriculture = form['agriculture'].value()
        item.economy = form['economy'].value()
        item.custom = form['custom'].value()
        item.education = form['education'].value()
        item.geography = form['geography'].value()
        item.siteid_id = form['siteid'].value()
        item.DataPage = form['DataPage'].value()
        item.nation = form['nation'].value()
        item.transportation = form['transportation'].value()
        item.police = form['police'].value()
        item.other = form['other'].value()
        item.religion = form['religion'].value()
        item.history = form['history'].value()
        item.mileage = form['mileage'].value()
        item.inputUser = form['inputUser'].value()
        item.save()
        s = req.FILES.getlist('picture')
        if s:
            for file in s:
                st = file.name
                imagepath = default_storage.save('himalaya/travelgraph/' + st, ContentFile(file.read()))
                pic = Travelgraph()
                pic.graph = 'himalaya/travelgraph/' + st
                pic.traverData_id = item.id
                pic.save()
        #获取要删除的图片，删除数据和图片
        dels = req.POST.get('pic')
        if(dels):
            dels = dels.split(',')
            if len(dels)!=0:
                for ite in dels:
                    rem = Travelgraph.objects.get(id = int(ite))
                    path = r'/media//' + rem.graph.name.encode('UTF-8')
                    if os.path.exists(path):
                        os.remove(path)
                    rem.delete()
        return redirect('../../?_rel_RouteName__id__exact='+str(item.RouteName_id))
    else:
        picture = dict()
        content = TravelData.objects.get(id=int(id))
        toa = content.toa
        toa =str(toa).replace('-','/')
        tol = content.tol
        tol =str(tol).replace('-','/')
        content.toa=toa
        content.tol=tol
        gra = Travelgraph.objects.filter(traverData=int(id))
        for item in gra:
            fileherf = r'/media/' + item.graph.name.encode("UTF-8")
            ids = str(item.id)
            picture[ids] = fileherf

        with open('creatree.pkl', 'rb') as file:
            ass = cPickle.load(file)
            file.close()
        data = ass[0]
        levelist = ass[1]
        addre = dict()
        for item in Site.objects.all():
            reg = item.region
            while (reg.id != 273):
                if str(reg.id) not in addre:
                    addre[str(reg.id)] = [(item.id, item.sitenameCH)]
                else:
                    addre[str(reg.id)].append((item.id, item.sitenameCH))
                reg = reg.pid

        # ------------------------------------------------------------实现按字母排序
        for key,value in addre.items():
            addre[key]=cnsortlist(value)

        # ----------------------------------------------------------实现按字母排序结束
        return render_to_response('xadmin/himalaya/traveldata/update.html',{'form':content,'picture':picture,'data': json.dumps(data), 'level': levelist,'addre':json.dumps(addre)})


def traveldetail(req,id):
    picture = []
    content = TravelData.objects.get(id=int(id))
    gra = Travelgraph.objects.filter(traverData=int(id))
    for item in gra:
        fileherf = r'/media/' + item.graph.name.encode("UTF-8")
        picture.append(fileherf)
    return render_to_response('xadmin/himalaya/traveldata/detail.html',{'form':content,'picture':picture})

global region
def creatregion(id):
    it = Category.objects.get(id=id)
    tmp = dict()
    tmp['id'] = it.id
    tmp['attrName'] =it.attrName
    tmp['pid'] = it.pid_id
    region.append(tmp)
    data = Category.objects.filter(pid=id)
    if(data):
        for item in data:
            creatregion(item.id)

def siteadd(req):
    if(req.method=='POST'):
        site = Site()
        form = site_form(req.POST)
        site.sitenameCH = form['sitenameCH'].value()
        site.sitenameEN = form['sitenameEN'].value()

        data = req.POST.get('lnglat')
        data = data.split(',')
        site.longitude = float(data[0])
        site.latitude = float(data[1])
        if form['altitude'].value():
            site.altitude = float(str(form['altitude'].value()))
        level = req.POST.get('level')
        level =  range(0,len(level.split(',')))
        #zsy 添加 5-4 start
        if (form['sitenameEN'].value()==''):
            site.sitenameEN=pinyinconvert.hanzi(site.sitenameCH)
            print (site.sitenameEN)
        # zsy 添加 5-4 end
        for i in level:
            tmpd = req.POST.get('level_'+str(len(level)-i-1))
            if tmpd:
                site.region_id = int(tmpd)
                break
        try:
            Site.objects.get(sitenameCH=form['sitenameCH'].value(),region_id = site.region_id)
            messages.info(req, site.sitenameCH + '已存在!请检查后重新输入')
            return redirect('..', {})
        except:
            site.save()
            # with open('site_region.pkl',"w+b") as file:
            #     data = cPickle.load(file)
            #     item = site.region
            #     while (item.id != 273):
            #         if str(item.id) not in data:
            #             data[item.id] = [(site.id,site.sitenameCH)]
            #         else:
            #             data[item.id].append((site.id,site.sitenameCH))
            #         item = item.pid
            return redirect('..')
    else:
        with open('creatree.pkl', 'rb') as file:
            ass = cPickle.load(file)
            file.close()
        data = ass[0]
        levelist = ass[1]
        return render_to_response('xadmin/himalaya/site/add.html', {'data':json.dumps(data),'level':levelist,'context_instance':RequestContext(req)})


def siteupdate(req,id):
    site = Site.objects.get(id=int(id))
    if (req.method == 'POST'):
        form = site_form(req.POST)
        site.sitenameCH = form['sitenameCH'].value()
        site.sitenameEN = form['sitenameEN'].value()
        if form['altitude'].value():
            site.altitude = float(str(form['altitude'].value()))
        if form['longitude'].value():
            site.longitude = float(str(form['longitude'].value()))
        if form['latitude'].value():
            site.latitude = float(str(form['latitude'].value()))

        level = req.POST.get('list')
        level = level.strip('[')
        level = level.strip(']')
        level = level.split(',')
        level.reverse()

        #zsy 添加 5-4 start
        if (form['sitenameEN'].value()==''):
            site.sitenameEN=pinyinconvert.hanzi(site.sitenameCH)
            print (site.sitenameEN)
        # zsy 添加 5-4 end

        for item in level:
            item = item.strip()
            item = item.strip('\'')
            tmpd = req.POST.get(item)
            if tmpd:
                site.region_id = int(tmpd)
                break
        redent = Site.objects.filter(sitenameCH=site.sitenameCH,region_id = site.region_id)
        for item in redent:
            if(item.id!=site.id):
                messages.info(req, site.sitenameCH + '已存在,修改失败!')
                return redirect('../..', {})
        site.save()
        return redirect('../..')
    else:
        data = Category.objects.get(id=273 )

        select = []
        ids = []
        it = site.region
        while (it.id != 273):
            select.append(it.attrName)
            ids.append(it.id)
            it = it.pid

        ids.reverse()
        select.reverse()

        levelist = zip(ids,select)
        with open('creatree.pkl', 'rb') as file:
            ass = cPickle.load(file)
            file.close()
        data = ass[0]
        level = ass[1]
        if(len(levelist)<len(level)):
            for i in range(len(levelist),len(level)):
                levelist.append([0,'None'])
        return render_to_response('xadmin/himalaya/site/update.html', {'data':json.dumps(data),'list':level,'level':levelist,'context_instance':RequestContext(req),'site':site})

#QGIS2WEB

def gis_location(request):
    print 'gis_location'
    if request.GET.has_key('lat'):
        lng=request.GET['lng']
        lat=request.GET['lat']
        print 'lon,lat', lng, lat
    return render_to_response('xadmin/himalaya/site/gislocation.html/', {}, context_instance=RequestContext(request))


def travelist(request):
    traveldata = request.GET['_rel_RouteName__id__exact']
    data = TravelData.objects.filter(RouteName_id=int(traveldata))
    routname = Route.objects.get(id=int(traveldata))
    if request.method =="POST":
        if(request.POST.get('flag')=='del'):
            tmp = request.POST.getlist('_selected_action')
            for ide in tmp:
                item = TravelData.objects.get(id = int(ide))
                item.delete()
            tmpdata = TravelData.objects.filter(RouteName_id=int(traveldata))
            ss = {}
            for item in tmpdata:
                ss[item.id] = item.order
            ss = sorted(ss.items(), key=lambda d:d[1])
            for i,it in enumerate(ss):
                item = TravelData.objects.get(id=it[0])
                item.order = i
                item.save()
        else:
            result = request.POST.get('tmps')
            result = result.split(',')[1:]
            res = dict()
            for i,item in enumerate(result):
                res[item] = i
            for item in data:
                item.order = int(res[str(item.id)])
                item.save()
    ite = []
    ites = []
    for item in data:
        ite.append(item)
    data = sorted(ite,key = lambda x:x.order)
    ite = []
    for item in data:
        tmp = []
        site = Site.objects.get(id = item.siteid_id)
        tmp.append(float(site.longitude))
        tmp.append(float(site.latitude))
        ite.append(tmp)
        ites.append(site.sitenameCH)
    return render_to_response('xadmin/himalaya/traveldata/list.html',{"form":data,"ite":ite,'tripitem':json.dumps(ites),'traveldata':traveldata,'RouteName':routname})
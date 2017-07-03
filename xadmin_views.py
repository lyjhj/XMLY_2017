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
import sys
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




def filechoiceadd(req):
    if req.method == 'POST':
        form = ChoiceForm(req.POST)
        if form.is_valid():
            chooseid = form['choice'].value()
            if (int(chooseid) == -1):
                dynamicsubjectid = 0

            else:

                dynamicsubjectid = int(chooseid)
            # 跳转正确的界面
            global username
            username=req.user
            if(req.POST.get("select")=='swf'):
                return redirect(r"../swfupload/"+str(dynamicsubjectid))
            else:
                return redirect(r'../filebaseinfoadd/'+str(dynamicsubjectid), {'abc': form})

            # 测试界面
            # return redirect(r'../subjectinfoadd', {'abc': form})
    else:
        form = ChoiceForm()

    return render_to_response('xadmin/himalaya/filebaseinfo/add.html', {'abc': form,'username':req.user})


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
        if form.is_valid():
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
            print 'bbbbbbbbbbbbbbbbbbbbbkuozhanshuxing', addkuozhanshuxing
            # sstrnames动态创建表单的名字，并且创建对应的属性字段
            sstrnames = locals()
            for i in xrange(0, sstrnum):
                if (sstr[i].isMust):
                    sstrnames['sstr%s' % i] = forms.CharField(required=sstr[i].isMust, label=sstr[i].fieldName + '*',
                                                              help_text=sstr[i].promtInfo)
                else:
                    sstrnames['sstr%s' % i] = forms.CharField(required=sstr[i].isMust, label=sstr[i].fieldName,
                                                              help_text=sstr[i].promtInfo)

            iintnames = locals()
            for i in xrange(0, iintnum):
                if (iint[i].isMust):
                    iintnames['iint%s' % i] = forms.IntegerField(required=iint[i].isMust, label=iint[i].fieldName + '*',
                                                                 help_text=iint[i].promtInfo)
                else:
                    iintnames['iint%s' % i] = forms.IntegerField(required=iint[i].isMust, label=iint[i].fieldName,
                                                                 help_text=iint[i].promtInfo)

            ffloatnames = locals()
            for i in xrange(0, ffloatnum):
                if (ffloat[i].isMust):
                    ffloatnames['ffloat%s' % i] = forms.FloatField(required=ffloat[i].isMust,
                                                                   label=ffloat[i].fieldName + '*',
                                                                   help_text=ffloat[i].promtInfo)
                else:
                    ffloatnames['ffloat%s' % i] = forms.FloatField(required=ffloat[i].isMust, label=ffloat[i].fieldName,
                                                                   help_text=ffloat[i].promtInfo)

            ddatenames = locals()
            for i in xrange(0, ddatenum):
                if (ddate[i].isMust):
                    ddatenames['ddate%s' % i] = forms.DateField(required=ddate[i].isMust,
                                                                label=ddate[i].fieldName + '*',
                                                                help_text=ddate[i].promtInfo)
                else:
                    ddatenames['ddate%s' % i] = forms.DateField(required=ddate[i].isMust,
                                                                label=ddate[i].fieldName, help_text=ddate[i].promtInfo)

            bbooleannames = locals()
            for i in xrange(0, bbooleannum):
                if (bboolean[i].isMust):
                    bbooleannames['bboolean%s' % i] = forms.TypedChoiceField(required=bboolean[i].isMust,
                                                                             coerce=lambda x: x == 'True',
                                                                             choices=((False, 'False'), (True, 'True')),
                                                                             widget=forms.RadioSelect,
                                                                             label=bboolean[i].fieldName + '*',
                                                                             help_text=bboolean[i].promtInfo,
                                                                             initial=False)
                else:
                    bbooleannames['bboolean%s' % i] = forms.TypedChoiceField(required=bboolean[i].isMust,
                                                                             coerce=lambda x: x == 'True',
                                                                             choices=((False, 'False'), (True, 'True')),
                                                                             widget=forms.RadioSelect,
                                                                             label=bboolean[i].fieldName + '*',
                                                                             help_text=bboolean[i].promtInfo,
                                                                             initial=False)

            # 枚举类型的定义
            eenumnames = locals()
            for i in xrange(0, eenumnum):
                choicess = [()]
                fill_topic_tree(parent_id=eenum[i].corrAttri, choicess=choicess)
                if (len(choicess[0]) != 0):
                    if (eenum[i].isMust):
                        eenumnames['eenum%s' % i] = forms.ChoiceField(required=eenum[i].isMust,
                                                                      label=eenum[i].fieldName + '*',
                                                                      help_text=eenum[i].promtInfo,
                                                                      choices=tree_choices(eenum[i].corrAttri))
                    else:
                        eenumnames['eenum%s' % i] = forms.ChoiceField(required=eenum[i].isMust,
                                                                      label=eenum[i].fieldName,
                                                                      help_text=eenum[i].promtInfo,
                                                                      choices=kongtree_choices(eenum[i].corrAttri))

            # 树类型定义
            ttreenames = locals()
            for i in xrange(0, ttreenum):
                choicess = [()]
                fill_topic_tree(parent_id=ttree[i].corrAttri, choicess=choicess)
                if (len(choicess[0]) != 0):
                    if (ttree[i].isMust):
                        ttreenames['ttree%s' % i] = forms.ChoiceField(required=ttree[i].isMust,
                                                                      label=ttree[i].fieldName + '*',
                                                                      help_text=ttree[i].promtInfo,
                                                                      choices=tree_choices(ttree[i].corrAttri))
                    else:
                        ttreenames['ttree%s' % i] = forms.ChoiceField(required=ttree[i].isMust,
                                                                      label=ttree[i].fieldName,
                                                                      help_text=ttree[i].promtInfo,
                                                                      choices=kongtree_choices(ttree[i].corrAttri))


                        # if req.method == 'POST':
                        #     form = SujectThemeDynamicForm(req.POST)
                        #     if form.is_valid():
                        #         global sstr, iint, ffloat, ddate, bboolean, eenum, ttree
                        #         global sstrnum, iintnum, ffloatnum, ddatenum, bbooleannum, eenumnum, ttreenum
                        #         filebaseid =int(dynamicfilebaseid)
                        #         for i in range(0, sstrnum):
                        #             fileextend = FileExtendInfo()
                        #             fileextend.fileId = int(filebaseid)
                        #             fileextend.fieldId = int(sstr[i].id)
                        #             fileextend.filedValue = form['sstr%s' % i].value()
                        #             fileextend.save()
                        #         for i in range(0, iintnum):
                        #             fileextend = FileExtendInfo()
                        #             fileextend.fileId = filebaseid
                        #             fileextend.fieldId = iint[i].id
                        #             fileextend.filedValue = form['iint%s' % i].value()
                        #             fileextend.save()
                        #         for i in range(0, ffloatnum):
                        #             fileextend = FileExtendInfo()
                        #             fileextend.fileId = filebaseid
                        #             fileextend.fieldId = ffloat[i].id
                        #             fileextend.filedValue = form['ffloat%s' % i].value()
                        #             fileextend.save()
                        #         for i in range(0, ddatenum):
                        #             if (len(form['ddate%s' % i].value()) != 0):
                        #                 fileextend = FileExtendInfo()
                        #                 l = str(form['ddate%s' % i].value()).split('/')
                        #                 fileextend.fileId = filebaseid
                        #                 fileextend.fieldId = ddate[i].id
                        #                 fileextend.filedValue = datetime.strptime(''.join(l), "%Y%m%d").date()
                        #                 fileextend.save()
                        #             else:
                        #                 fileextend = FileExtendInfo()
                        #                 fileextend.fileId = filebaseid
                        #                 fileextend.fieldId = ddate[i].id
                        #                 fileextend.filedValue = form['ddate%s' % i].value()
                        #                 fileextend.save()
                        #         for i in range(0, bbooleannum):
                        #             fileextend = FileExtendInfo()
                        #             fileextend.fileId = filebaseid
                        #             fileextend.fieldId = bboolean[i].id
                        #             fileextend.filedValue = form['bboolean%s' % i].value()
                        #             fileextend.save()
                        #         for i in range(0, eenumnum):
                        #             choicess = [()]
                        #             fill_topic_tree(parent_id=eenum[i].corrAttri, choicess=choicess)
                        #             if ((len(choicess[0]) != 0) and (len(form['eenum%s' % i].value()) != 0)):
                        #                 fileextend = FileExtendInfo()
                        #                 fileextend.fileId = filebaseid
                        #                 fileextend.fieldId = eenum[i].id
                        #                 fileextend.filedValue = form['eenum%s' % i].value()
                        #                 fileextend.save()
                        #         for i in range(0, ttreenum):
                        #             choicess = [()]
                        #             fill_topic_tree(parent_id=ttree[i].corrAttri, choicess=choicess)
                        #             if ((len(choicess[0]) != 0) and len(form['ttree%s' % i].value()) != 0):
                        #                 fileextend = FileExtendInfo()
                        #                 fileextend.fileId = filebaseid
                        #                 fileextend.fieldId = ttree[i].id
                        #                 fileextend.filedValue = form['ttree%s' % i].value()
                        #                 fileextend.save()



                        # 添加时候已经有了处理

    if req.method == 'POST':
        form = SujectThemeDynamicForm(req.POST,req.FILES)
        if form.is_valid():
            newfbs=FileBaseInfo.objects.all().filter(title__exact=req.session.get('title',default=None)).filter(filecode__exact=req.session.get('filecode',default=None)).filter(creator__exact
                                                =req.session.get('creator',default=None)).filter(keywords__exact=req.session.get('keywords',default=None)).filter(description__exact=req.session.get('description',default=None)).filter(publisher__exact=req.session.get('publisher',default=None)).filter(subjecttype=int(dynamicfilebaseid))
            print 'yyyyyyyyyyyyyyyy',newfbs
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

                dynamicfilebaseid = fbii.id
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
            for i in range(0, eenumnum):
                choicess = [()]
                fill_topic_tree(parent_id=eenum[i].corrAttri, choicess=choicess)
                if ((len(choicess[0]) != 0) and (len(form['eenum%s' % i].value()) != 0)):
                    if (len(FileExtendInfo.objects.filter(fileId=filebaseid).filter(fieldId=eenum[i].id)) == 0):
                        fileextendupdate = FileExtendInfo()
                        fileextendupdate.fileId = filebaseid
                        fileextendupdate.fieldId = eenum[i].id
                        fileextendupdate.filedValue = form['eenum%s' % i].value()
                        fileextendupdate.save()
                    else:
                        fileextendupdate = FileExtendInfo.objects.filter(fileId=filebaseid).get(fieldId=eenum[i].id)
                        fileextendupdate.filedValue = form['eenum%s' % i].value()
                        fileextendupdate.save()
            for i in range(0, ttreenum):
                choicess = [()]
                fill_topic_tree(parent_id=ttree[i].corrAttri, choicess=choicess)
                if ((len(choicess[0]) != 0) and len(form['ttree%s' % i].value()) != 0):
                    if (len(FileExtendInfo.objects.filter(fileId=filebaseid).filter(fieldId=ttree[i].id)) == 0):
                        fileextendupdate = FileExtendInfo()
                        fileextendupdate.fileId = filebaseid
                        fileextendupdate.fieldId = ttree[i].id
                        fileextendupdate.filedValue = form['ttree%s' % i].value()
                        fileextendupdate.save()
                    else:
                        fileextendupdate = FileExtendInfo.objects.filter(fileId=filebaseid).get(fieldId=ttree[i].id)
                        fileextendupdate.filedValue = form['ttree%s' % i].value()
                        fileextendupdate.save()

            # 添加成功跳转
            messages.info(req, '专题文献成功')
            return redirect(r'../..', {})
    else:
        form = SujectThemeDynamicForm()
    global addkuozhanshuxing
    print 'ccccccccccccccccckuozhanshuxing',addkuozhanshuxing
    print 'dddddddddd',req.session.get('picture',default=None)
    return render_to_response('xadmin/himalaya/filebaseinfo/subjectinfoadd.html',
                              {'form': form, 'categories': Category.objects.filter(pid_id=None),'kuozhanshuxing':addkuozhanshuxing,'username':req.user})



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
        formupdate.contentLength = formnew['contentLength'].value()
        formupdate.uploadPeople = formnew['uploadPeople'].value()
        # formupdate.updateDate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        if (len(str(formnew['picture'].value()).split('.')) == 2):
            s = formupdate.picture
            s = './media/' + str(s)
            s = s.decode('utf-8')
            os.remove(s)
            formupdate.picture = formnew['picture'].value()
        if (len(str(formnew['attachment'].value()).split('.')) == 2):
            s1 = formupdate.attachment
            s = './media/' + str(s1)
            s = s.decode('utf-8')
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
def fileextendinfoedit(req, id):
    # 动态生成表单
    sujectidd = FileBaseInfo.objects.get(id=int(id)).subjecttype
    global editkuozhanshuxing
    editkuozhanshuxing=True
    class SujectThemeDynamicForm(forms.Form):
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
                sstrnames['sstr%s' % i] = forms.CharField(required=True, label=sstr[i].fieldName + '*',
                                                          help_text=sstr[i].promtInfo, initial=initvalue,
                                                          error_messages={'required': '必须填写'})
            else:
                sstrnames['sstr%s' % i] = forms.CharField(required=sstr[i].isMust, label=sstr[i].fieldName,
                                                          help_text=sstr[i].promtInfo, initial=initvalue)

        iintnames = locals()
        for i in xrange(0, iintnum):
            initvalue = ''
            if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=iint[i].id)) != 0):
                initvalue = FileExtendInfo.objects.filter(fileId=id).get(fieldId=iint[i].id).filedValue
            if (iint[i].isMust):
                iintnames['iint%s' % i] = forms.IntegerField(required=iint[i].isMust, label=iint[i].fieldName + '*',
                                                             help_text=iint[i].promtInfo, initial=initvalue)
            else:
                iintnames['iint%s' % i] = forms.IntegerField(required=iint[i].isMust, label=iint[i].fieldName,
                                                             help_text=iint[i].promtInfo, initial=initvalue)

        ffloatnames = locals()
        for i in xrange(0, ffloatnum):
            initvalue = ''
            if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=ffloat[i].id)) != 0):
                initvalue = FileExtendInfo.objects.filter(fileId=id).get(fieldId=ffloat[i].id).filedValue
            if (ffloat[i].isMust):
                ffloatnames['ffloat%s' % i] = forms.FloatField(required=ffloat[i].isMust,
                                                               label=ffloat[i].fieldName + '*',
                                                               help_text=ffloat[i].promtInfo, initial=initvalue)
            else:
                ffloatnames['ffloat%s' % i] = forms.FloatField(required=ffloat[i].isMust, label=ffloat[i].fieldName,
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
                    eenumnames['eenum%s' % i] = forms.ChoiceField(required=eenum[i].isMust,
                                                                  label=eenum[i].fieldName + '*',
                                                                  help_text=eenum[i].promtInfo,
                                                                  choices=tree_choices(eenum[i].corrAttri),
                                                                  initial=initvalue)
                else:
                    eenumnames['eenum%s' % i] = forms.ChoiceField(required=eenum[i].isMust,
                                                                  label=eenum[i].fieldName,
                                                                  help_text=eenum[i].promtInfo,
                                                                  choices=kongtree_choices(eenum[i].corrAttri),
                                                                  initial=initvalue)

        # 树类型定义
        ttreenames = locals()
        for i in xrange(0, ttreenum):
            choicess = [()]
            fill_topic_tree(parent_id=ttree[i].corrAttri, choicess=choicess)

            if (len(choicess[0]) != 0):
                initvalue = ''
                if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=ttree[i].id)) != 0):
                    initvalue = FileExtendInfo.objects.filter(fileId=id).get(fieldId=ttree[i].id).filedValue
                if (ttree[i].isMust):
                    ttreenames['ttree%s' % i] = forms.ChoiceField(required=ttree[i].isMust,
                                                                  label=ttree[i].fieldName + '*',
                                                                  help_text=ttree[i].promtInfo,
                                                                  choices=tree_choices(ttree[i].corrAttri),
                                                                  initial=initvalue)
                else:
                    ttreenames['ttree%s' % i] = forms.ChoiceField(required=ttree[i].isMust,
                                                                  label=ttree[i].fieldName,
                                                                  help_text=ttree[i].promtInfo,
                                                                  choices=kongtree_choices(ttree[i].corrAttri),
                                                                  initial=initvalue)

    if req.method == 'POST':
        form = SujectThemeDynamicForm(req.POST)
        if form.is_valid():
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
                choicess = [()]
                fill_topic_tree(parent_id=ttree[i].corrAttri, choicess=choicess)
                if ((len(choicess[0]) != 0) and len(form['ttree%s' % i].value()) != 0):
                    if (len(FileExtendInfo.objects.filter(fileId=id).filter(fieldId=ttree[i].id)) == 0):
                        fileextendupdate = FileExtendInfo()
                        fileextendupdate.fileId = id
                        fileextendupdate.fieldId = ttree[i].id
                        fileextendupdate.filedValue = form['ttree%s' % i].value()
                        fileextendupdate.save()
                    else:
                        fileextendupdate = FileExtendInfo.objects.filter(fileId=id).get(fieldId=ttree[i].id)
                        fileextendupdate.filedValue = form['ttree%s' % i].value()
                        fileextendupdate.save()

            # 添加成功跳转
            messages.info(req, '专题文献修改成功')
            return redirect(r'../../../filebaseinfo/', {})

    try:
        form = SujectThemeDynamicForm()
        global editkuozhanshuxing
        print 'bbbbbbbbb',editkuozhanshuxing
    except View.DoesNotExist:
        return render_to_response('xadmin/404.html', {})
    return render_to_response('xadmin/himalaya/filebaseinfo/fileextendinfoupdate.html',
                              {'form': form,'editkuozhanshuxing':editkuozhanshuxing,'username':req.user})


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

        formextend=FileExtendInfo.objects.filter(fileId=id)
        formextkey=[]
        formextval=[]
        for dd in formextend:

            formextkey.append(SubjectTheme.objects.get(id=int(dd.fieldId)).fieldName)
            if(((dd.filedValue=='-1') and (int(SubjectTheme.objects.get(id=int(dd.fieldId)).fieldType)==5)) or
                   ((dd.filedValue == '-1') and (int(SubjectTheme.objects.get(id=int(dd.fieldId)).fieldType) == 6))):
                formextval.append('null')
            elif((int(SubjectTheme.objects.get(id=int(dd.fieldId)).fieldType)==5) or (int(SubjectTheme.objects.get(id=int(dd.fieldId)).fieldType)==6)):
                print dd.filedValue
                formextval.append(Category.objects.get(id=int(dd.filedValue)))
            else:
                formextval.append(dd.filedValue)
        formextenddetail=zip(formextkey,formextval)
        return render_to_response('xadmin/himalaya/filebaseinfo/detail.html',
                              {'form': form, 'formextenddetail':formextenddetail,'strfiletype': strfiletype, 'strlan': strlan, 'strdis': strdis,
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
            viewi.viewPlace = form['viewPlace'].value()
            viewi.save()
            viewii = View.objects.all()[len(View.objects.all()) - 1]
            # 解压需要的文件名
            filename = r'./media/' + viewii.viewPath.name
            # 解压需要放的路径,l[0]表示去掉扩展名的文件路径
            l = viewii.viewPath.name.split('.')
            filenewname = r'./media/' + l[0]
            # 解压
            unzip_file(filename, filenewname)
            # 更改View表中的路径，更改到文件夹下，ll【0】表示获得用户上传的文件名
            # 查找Index.Html路径
            search(filenewname, 'index.html')  # 获取到的路径：类似./media/himalaya/quanjing/Jiuzhaigou_W74ssR2\output\index.html
            viewii.viewPath.name = viewpathstr.split('media/')[1].replace('\\', r'/')
            viewii.save()
            messages.info(req, '保存成功')
            return redirect('..', {})
    else:
        form = ViewForm()

    return render_to_response('xadmin/himalaya/view/add.html', {'form': form,'username':req.user})


# view的修改页面
def viewedite(req, id):
    if req.method == 'POST':

        formnew = ViewForm(req.POST, req.FILES)
        if ((len(str(formnew['viewPath'].value()).split('.')) == 2) and (
            str(formnew['viewPath'].value()).split('.')[1] != 'zip')):
            messages.add_message(req, 1,'请上传.zip文件')
        elif ((len(str(formnew['viewPath'].value()).split('.')) != 2) or (str(formnew['viewPath'].value()).split('.')[1] == 'zip')):
            viewupdate = View.objects.get(id=int(id))
            viewupdate.viewName = formnew['viewName'].value()
            viewupdate.viewEqu = formnew['viewEqu'].value()
            viewupdate.viewAuth = formnew['viewAuth'].value()
            viewupdate.viewPlace = formnew['viewPlace'].value()
            viewupdate.viewIntro = formnew['viewIntro'].value()
            createdate = str(formnew['createDate'].value()).split('/')
            if (len(createdate) == 3):
                viewupdate.createDate = datetime.strptime(''.join(createdate), "%Y%m%d").date()
            if (len(str(formnew['viewPic'].value()).split('.')) == 2):
                s1 = viewupdate.viewPic
                s1 = str(s1)
                s1 = s1.decode('utf-8')
                os.remove('./media/' + str(s1))
                viewupdate.viewPic = formnew['viewPic'].value()
            if (len(str(formnew['viewPath'].value()).split('.')) == 2):
                s = viewupdate.viewPath
                s = str(s).split("/")
                str1 = s[0:3]
                str1 = '/'.join(str1)
                str1 = str1.decode('utf-8')
                shutil.rmtree('./media/' + str1)
                os.remove('./media/' + str1 + '.zip')
                viewupdate.viewPath = formnew['viewPath'].value()
            viewupdate.save()
            if (len(str(formnew['viewPath'].value()).split('.')) == 2):
                # 解压文件
                viewii = View.objects.get(id=int(id))
                # 解压需要的文件名
                filename = r'./media/' + viewii.viewPath.name
                # 解压需要放的路径,l[0]表示去掉扩展名的文件路径
                l = viewii.viewPath.name.split('.')
                clientSystem = req.META['HTTP_USER_AGENT']
                # 如果是windows则按cp936编码, 否则按utf - 8编码
                filenewname = r'./media/' + l[0]
                # 解压
                unzip_file(filename, filenewname)
                # 更改View表中的路径，更改到文件夹下，ll【0】表示获得用户上传的文件名
                # 查找Index.Html路径
                search(filenewname,
                       'index.html')  # 获取到的路径：类似./media/himalaya/quanjing/Jiuzhaigou_W74ssR2\output\index.html
                viewii.viewPath.name = viewpathstr.split('media/')[1].replace('\\', r'/')
                viewii.save()
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
        Category.objects.filter(id=idnum).update(attrName=name)

    if opt== '1':
        idnum = request.POST.get('id')
        print idnum
        Category.objects.filter(id=idnum).delete()

    if opt=='2':
        name = request.POST.get('name')
        pname = request.POST.get('pname')
        if pname == '-1':
            pname=0
        try:
            Category.objects.get(attrName=name, pid=pname)
            return HttpResponse(json.dumps({"data": "-2"}))
        except ObjectDoesNotExist:
            data = Category(attrName=name,pid_id=pname)
            data.save()
            data = Category.objects.get(attrName=name, pid=pname)
            id = data.id
            return HttpResponse(json.dumps({"data": id}))

    if opt == '3':
        name = request.POST.get('name')
        pname = request.POST.get('id')
        if pname == '-1':
            pname = 0
        try:
            Category.objects.get(attrName=name, pid=pname)
            return HttpResponse(json.dumps({"data": "-2"}))
        except ObjectDoesNotExist:
            data = Category(attrName=name, pid_id=pname)
            data.save()
            data = Category.objects.get(attrName=name, pid=pname)
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
    many = FileBaseInfo._meta.many_to_many
    value = [('-1', '---------')]
    flage = {}
    flage['-1'] = -1
    for field in fields:
        if (field.name != 'subjecttype' and field.name != 'id' and field.name != 'uploadDate' and field.name != 'updateDate' and field.name != 'size' and field.name != 'contentLength'):
            flage[field.name] = 0
            value.append((field.name, field.verbose_name))
    for field in many:
        flage[field.name] = 2
        value.append((field.name, field.verbose_name))
    dynamicfilebaseid = int(dynamicfilebaseid)
    if (dynamicfilebaseid == -1):
        pass
    else:
        extend = SubjectTheme.objects.filter(subjectId=dynamicfilebaseid)
        for field in extend:
            value.append((field.id, field.fieldName))
            flage[str(field.id)] = 1

    class swfForm(forms.Form):
        eenumnames = locals()
        eenum = len(data)
        for i in range(len(data)):
            eenumnames['data%s' % i] = forms.ChoiceField(label=data[i],
                                                         choices=value)
        i = len(data)
        eenumnames["data%s" % i] = forms.FileField(label=u'缩略图')
        i = i + 1
        eenumnames["data%s" % i] = forms.FileField(label=u'附件')

    if request.method == 'POST':
        form = swfForm(request.POST, request.FILES)
        dict = []
        if (dynamicfilebaseid != -1 and dynamicfilebaseid != 0):
            subject = Subject.objects.get(id=int(dynamicfilebaseid))
            subjecttype = subject.subjectName
            spath = os.path.normpath('./media/himalaya/files/' + subjecttype)
            if not os.path.exists(spath) or not os.path.isdir(spath):
                os.mkdir('./media/himalaya/files/' + subjecttype)
            spath = os.path.normpath('./media/himalaya/images/' + subjecttype)
            if not os.path.exists(spath) or not os.path.isdir(spath):
                os.mkdir('./media/himalaya/images/' + subjecttype)
        s = request.FILES.get('data%s' % len(data))
        picturepath = -1
        attachpath = -1
        if s:
            st = s.name
            imagepath = default_storage.save('himalaya/images/' + str(st), ContentFile(s.read()))
            # if(GetFileNameAndExt(imagepath)=='rar'):
            #     # file = rarfile.RarFile(imagepath)  # 这里写入的是需要解压的文件，别忘了加路径
            #     # file.extractall('./media/himalaya/images/'+subjecttype)
            # if (GetFileNameAndExt(imagepath) == 'zip'):
            if (os.path.isfile('./media/' + imagepath)):
                f = zipfile.ZipFile('./media/' + imagepath, 'r')
                for file in f.namelist():
                    f.extract(file, './media/himalaya/images/')
                picturepath = './media/himalaya/images/' + f.namelist()[0]
                os.remove('./media/' + imagepath)
            else:
                print 'not found'
        s = request.FILES.get('data%s' % (len(data) + 1))
        if s:
            st = s.name
            attachpath1 = default_storage.save('./himalaya/files/' + str(st), ContentFile(s.read()))
            # if (GetFileNameAndExt(attachpath) == 'rar'):
            #     file = rarfile.RarFile(attachpath)  # 这里写入的是需要解压的文件，别忘了加路径
            #     file.extractall('./media/himalaya/files/' + subjecttype)
            # if (GetFileNameAndExt(attachpath) == 'zip'):
            if (os.path.isfile('./media/' + attachpath1)):
                f = zipfile.ZipFile('./media/' + attachpath1, 'r')
                for file in f.namelist():
                    f.extract(file, './media/himalaya/files/')
                attachpath = './media/himalaya/files/' + f.namelist()[0]
                os.remove('./media/' + attachpath1)
            else:
                print 'not found'
        for i in range(len(data)):
            s = form['data%s' % i].value()
            dict.append(s)
        nrows = table.nrows
        repetition = []
        for i in range(1, nrows):
            if (table.cell(i, 0).value):
                try:
                    fbi = FileBaseInfo.objects.get(filecode=table.cell(i, 0).value)
                    extend = {}
                    manytomany = {}
                    for j in range(len(data)):
                        s = dict[j]
                        if (s!=-1):
                            if (int(flage[s]) == 0):
                                # mt = fbi._meta.get_field(s)
                                if (type(fbi._meta.get_field(s)) == django.db.models.fields.DateField):
                                    date = table.cell(i, j).value
                                    m = date.decode('utf-8').split(u"年".decode('utf-8'))
                                    year = m[0]
                                    if (len(m) > 1 and u"月".decode('utf-8') in m[1]):
                                        m = m[1].split(u"月".decode('utf-8'))
                                        month = m[0]
                                        if (len(m) > 1 and u"日".decode('utf-8') in m[1]):
                                            m = m[1].split(u"日".decode('utf-8'))
                                            day = m[0]
                                        else:
                                            day = '01'
                                    else:
                                        month = '01'
                                        day = '01'
                                    date = str(year) + str(month) + str(day)
                                    date = datetime.strptime(''.join(date), "%Y%m%d").date()
                                    setattr(fbi, s, date)
                                else:
                                    setattr(fbi, s, table.cell(i, j).value)
                            elif (int(flage[s]) == 1):
                                extend[s] = table.cell(i, j).value
                            elif (int(flage[s]) == 2):
                                manytomany[s] = table.cell(i, j).value
                    flagp = 0
                    if(attachpath!=-1):
                        for file in os.listdir(attachpath):
                            sstr1 = os.path.join('./media/himalaya/files/', subjecttype, file)
                            str1 = file.split('.')
                            if (str(str1[0]) == table.cell(i, 0).value):
                                flagp = 1
                                sourcecpy(os.path.join(attachpath, file), './media/himalaya/files/' + subjecttype)
                                fbi.attachment = 'himalaya/files/' + subjecttype + '/' + file
                                fbi.size = os.path.getsize(sstr1)
                                if (str1[1] == 'pdf'):
                                    pdf = PdfFileReader(open(sstr1, "r"))
                                    fbi.contentLength = pdf.getNumPages()
                            if (flagp == 0):
                                fbi.attachment = ''
                    flagp = 0
                    if(picturepath!=-1):
                        for file in os.listdir(picturepath):
                            sstr1 = os.path.join('./media/himalaya/images/', subjecttype, file)
                            str1 = file.split('.')
                            if (str(str1[0]) == table.cell(i, 0).value):
                                flagp = 1
                                sourcecpy(os.path.join(picturepath, file), './media/himalaya/images/' + subjecttype)
                                fbi.picture = 'himalaya/images/' + subjecttype + '/' + file
                            if (flagp == 0):
                                fbi.picture = ''
                    fbi.save()
                    for item in manytomany:
                        mt = fbi._meta.get_field(item)
                        m = mt.related_model
                        itemstr = manytomany[item]
                        mod = m.objects.all()
                        for v in mod:
                            if (str(v) == itemstr):
                                s = 'FileBaseInfo_' + item
                                modelnames = apps.get_app_config('himalaya').get_model(s)
                                try:
                                    modelname = modelnames.objects.get(filebaseinfo_id=fbi.id)
                                except ObjectDoesNotExist:
                                    modelnames = apps.get_app_config('himalaya').get_model(s)
                                    modelname = modelnames()
                                    setattr(modelname, "filebaseinfo_id", int(fbi.id))
                                setattr(modelname, m._meta.model_name + '_id', int(v.id))
                                modelname.save()
                    if (dynamicfilebaseid != -1):
                        for item in extend:
                            try:
                                fextend = FileExtendInfo.objects.get(fileId=fbi.id,fieldId=int(item))
                            except ObjectDoesNotExist:
                                fextend = FileExtendInfo()
                                fextend.fileId = fbi.id
                                fextend.fieldId = int(item)
                            if (int(SubjectTheme.objects.get(id=int(item)).fieldType) == 6 or int(
                                    SubjectTheme.objects.get(id=int(item)).fieldType) == 5):
                                pid = SubjectTheme.objects.get(id=int(item)).corrAttri
                                global featureid
                                featureid = None
                                checktrees(int(pid), extend[item])
                                if featureid!=None:
                                    fextend.filedValue = featureid
                                else:
                                    print 'extendvalue', fbi.id, item, extend[item]
                                    fextend.filedValue = 'NULL'
                            else:
                                fextend.filedValue = extend[item]
                            fextend.save()
                    print table.cell(i, 0).value, 'success'
                except ObjectDoesNotExist:
                    repetition.append(str(table.cell(i, 0).value))
        if(attachpath!=-1):
            shutil.rmtree(attachpath)
        if(picturepath!=-1):
            shutil.rmtree(picturepath)
        print repetition
        if(len(repetition)!=0):
            redirect('/xadmin/himalaya/modifyaddr/')
        else:
            print 'guokena'
            redirect("../")
    else:
        form = swfForm()
    return render_to_response("xadmin/himalaya/filebaseinfo/swfmodify.html", {"form": form})

def modifyaddr(request):
    data = request.session.get('repetition')
    if (request.method == "POST"):
        redirect('/xadmin/himalaya/filebaseinfo/')
    return render_to_response("xadmin/himalaya/filebaseinfo/modifyaddr.html", {"data": data})

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

def swfchoice(request):
    path = request.session.get('path')
    dynamicfilebaseid = request.session.get('dynamicfilebaseid')
    ss = xlrd.open_workbook(path)
    table = ss.sheets()[0]
    data = table.row_values(0)
    fields = FileBaseInfo._meta.get_fields()
    many = FileBaseInfo._meta.many_to_many
    value = [('-1','---------')]
    flage = {}
    flage['-1'] = -1
    for field in fields:
        if (field.name != 'subjecttype' and field.name != 'id' and field.name != 'uploadDate' and field.name != 'updateDate' and field.name !='size' and field.name!='contentLength'):
                flage[field.name] = 0
                value.append((field.name,field.verbose_name))
    for field in many:
        flage[field.name] = 2
        value.append((field.name,field.verbose_name))
    dynamicfilebaseid = int(dynamicfilebaseid)
    if (dynamicfilebaseid == -1):
        pass
    else:
        extend = SubjectTheme.objects.filter(subjectId=dynamicfilebaseid)
        for field in extend:
            value.append((field.id, field.fieldName))
            flage[str(field.id)] = 1
    class swfForm(forms.Form):
            eenumnames = locals()
            eenum = len(data)
            for i in range(len(data)):
                eenumnames['data%s' % i] = forms.ChoiceField(label=data[i],
                                                              choices=value)
            i = len(data)
            eenumnames["data%s" % i] = forms.FileField(label=u'缩略图')
            i = i + 1
            eenumnames["data%s" % i] = forms.FileField(label=u'附件')
    if request.method =='POST':
        form = swfForm(request.POST, request.FILES)
        dict = []
        if(dynamicfilebaseid!=-1 and dynamicfilebaseid!=0):
            subject = Subject.objects.get(id=int(dynamicfilebaseid))
            subjecttype = subject.subjectName
            spath = os.path.normpath('./media/himalaya/files/'+subjecttype)
            if not os.path.exists(spath) or not os.path.isdir(spath):
                os.mkdir('./media/himalaya/files/'+subjecttype)
            spath =  os.path.normpath('./media/himalaya/images/'+subjecttype)
            if not os.path.exists(spath) or not os.path.isdir(spath):
                os.mkdir('./media/himalaya/images/'+subjecttype)
        s = request.FILES.get('data%s' % len(data))
        if s:
            st = s.name
            imagepath = default_storage.save('himalaya/images/'+str(st), ContentFile(s.read()))
            # if(GetFileNameAndExt(imagepath)=='rar'):
            #     # file = rarfile.RarFile(imagepath)  # 这里写入的是需要解压的文件，别忘了加路径
            #     # file.extractall('./media/himalaya/images/'+subjecttype)
            # if (GetFileNameAndExt(imagepath) == 'zip'):
            if(os.path.isfile('./media/'+imagepath)):
                f = zipfile.ZipFile('./media/'+imagepath, 'r')
                for file in f.namelist():
                    f.extract(file, './media/himalaya/images/')
                picturepath = './media/himalaya/images/'+f.namelist()[0]
                os.remove('./media/'+imagepath)
            else:
                print 'not found'
        s = request.FILES.get('data%s' % (len(data) + 1))
        if s:
            st = s.name
            attachpath1 = default_storage.save('./himalaya/files/' + str(st), ContentFile(s.read()))
            # if (GetFileNameAndExt(attachpath) == 'rar'):
            #     file = rarfile.RarFile(attachpath)  # 这里写入的是需要解压的文件，别忘了加路径
            #     file.extractall('./media/himalaya/files/' + subjecttype)
            # if (GetFileNameAndExt(attachpath) == 'zip'):
            if(os.path.isfile('./media/'+attachpath1)):
                f = zipfile.ZipFile('./media/'+attachpath1, 'r')
                for file in f.namelist():
                    f.extract(file, './media/himalaya/files/')
                attachpath = './media/himalaya/files/'+f.namelist()[0]
                os.remove('./media/'+attachpath1)
            else:
                print 'not found'
        for i in range(len(data)):
            s = form['data%s' % i].value()
            dict.append(s)
        nrows = table.nrows
        repetition = []
        for i in range(1, nrows):
            if(table.cell(i, 0).value):
                try:
                    FileBaseInfo.objects.get(filecode=table.cell(i, 0).value)
                    repetition.append(str(table.cell(i, 0).value))
                except ObjectDoesNotExist:
                    fbi = FileBaseInfo()
                    extend = {}
                    manytomany = {}
                    fbi.uploadPeople = 'admin'
                    for j in range(len(data)):
                        s = dict[j]
                        if table.cell(i, j).value:
                            if (int(flage[s]) == 0):
                                # mt = fbi._meta.get_field(s)
                                if (type(fbi._meta.get_field(s)) == django.db.models.fields.DateField):
                                    date = table.cell(i, j).value
                                    m = date.decode('utf-8').split(u"年".decode('utf-8'))
                                    year = m[0]
                                    if (len(m) > 1 and u"月".decode('utf-8') in m[1]):
                                        m = m[1].split(u"月".decode('utf-8'))
                                        month = m[0]
                                        if (len(m) > 1 and u"日".decode('utf-8') in m[1]):
                                            m = m[1].split(u"日".decode('utf-8'))
                                            day = m[0]
                                        else:
                                            day = '01'
                                    else:
                                        month = '01'
                                        day = '01'
                                    date = str(year) + str(month) + str(day)
                                    date = datetime.strptime(''.join(date), "%Y%m%d").date()
                                    setattr(fbi, s, date)
                                else:
                                    setattr(fbi, s, table.cell(i, j).value)
                            elif (int(flage[s]) == 1):
                                extend[s] = table.cell(i, j).value
                            elif (int(flage[s]) == 2):
                                manytomany[s] = table.cell(i, j).value
                        else:
                            if(int(flage[s]) ==0):
                                setattr(fbi,s,'NULL')
                    setattr(fbi, 'subjecttype', dynamicfilebaseid)
                    flagp=0
                    for file in os.listdir(attachpath):
                        sstr1 = os.path.join('./media/himalaya/files/', subjecttype, file)
                        str1 = file.split('.')
                        if(str(str1[0])==table.cell(i,0).value):
                            flagp=1
                            sourcecpy(os.path.join(attachpath,file), './media/himalaya/files/' + subjecttype)
                            fbi.attachment='himalaya/files/' +subjecttype+'/'+file
                            fbi.size = os.path.getsize(sstr1)
                            if(str1[1]=='pdf'):
                                pdf = PdfFileReader(open(sstr1, "r"))
                                fbi.contentLength = pdf.getNumPages()
                        if(flagp==0):
                            fbi.attachment=''
                    flagp = 0
                    for file in os.listdir(picturepath):
                        sstr1 = os.path.join('./media/himalaya/images/', subjecttype, file)
                        str1 = file.split('.')
                        if (str(str1[0]) == table.cell(i, 0).value):
                            flagp = 1
                            sourcecpy(os.path.join(picturepath,file), './media/himalaya/images/' + subjecttype)
                            fbi.picture = 'himalaya/images/' + subjecttype + '/' + file
                        if(flagp==0):
                            fbi.picture = ''
                    fbi.save()
                    st = FileBaseInfo.objects.get(id=fbi.id)
                    for item in manytomany:
                        mt = st._meta.get_field(item)
                        m = mt.related_model
                        itemstr = manytomany[item]
                        mod = m.objects.all()
                        for v in mod:
                            if (str(v) == itemstr):
                                s = 'FileBaseInfo_' + item
                                modelnames = apps.get_app_config('himalaya').get_model(s)
                                modelname = modelnames()
                                setattr(modelname, "filebaseinfo_id", int(st.id))
                                setattr(modelname, m._meta.model_name + '_id', int(v.id))
                                modelname.save()
                    if (dynamicfilebaseid != -1):
                        for item in extend:
                            fextend = FileExtendInfo()
                            fextend.fileId = fbi.id
                            fextend.fieldId = int(item)
                            if (int(SubjectTheme.objects.get(id=int(item)).fieldType) == 6 or int(
                                    SubjectTheme.objects.get(id=int(item)).fieldType) == 5):
                                pid = SubjectTheme.objects.get(id=int(item)).corrAttri
                                global featureid
                                featureid = None
                                checktrees(int(pid), extend[item])
                                if featureid!=None:
                                    fextend.filedValue = featureid
                                else:
                                    print 'extendvalue',fbi.id,item,extend[item]
                                    fextend.filedValue = 'NULL'
                            else:
                                fextend.filedValue = extend[item]
                            fextend.save()
                    print table.cell(i, 0).value, 'success'
        shutil.rmtree(attachpath)
        shutil.rmtree(picturepath)
        print repetition
        if(len(repetition)!=0):
            redirect('/xadmin/himalaya/swfaddr/')
        else:
            redirect('../')
    else:
        form = swfForm()
    return render_to_response("xadmin/himalaya/filebaseinfo/swfchoice.html",{"form": form})
# return render_to_response("xadmin/himalaya/filebaseinfo/swfchoice.html",{"form":form,"flage":json.dumps(flage),"path":path,"dynamic":dynamicfilebaseid})

def swfaddr(request):
    data = request.session.get('repetition')
    if(request.method=="POST"):
        return redirect("/xadmin/himalaya/filebaseinfo/")
    return render_to_response("xadmin/himalaya/filebaseinfo/swfaddr.html",{"data":data})
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







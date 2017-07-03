# -*- coding: utf-8 -*-
# !/usr/bin/env python

from __future__ import unicode_literals

from django.db import models

from datetime import datetime

# Create your models here.

'''
The file type model
文件类型
'''


class FileType(models.Model):
    fileTypeName = models.CharField(max_length=50, verbose_name='类型名称', unique=True)
    sortNum = models.IntegerField(verbose_name='排序', default=0, blank=True, editable=False)

    def __unicode__(self):
        return self.fileTypeName

    class Meta:
        verbose_name = '文件类型'
        verbose_name_plural = verbose_name


'''class FileType(models.Model):
    fileTypeName = models.CharField(max_length=50, verbose_name='类型名称', unique=True)
    sortNum = models.IntegerField(verbose_name='排序', default=0,blank=True)

    def __unicode__(self):
        return self.fileTypeName

    class Meta:
        verbose_name = '文件类型'
        verbose_name_plural = verbose_name'''

'''
The file's spatial scope model
空间范围
'''


class SpaceScope(models.Model):
    spcaeTypeName = models.CharField(max_length=50, verbose_name='类型名称', unique=True)
    sortNum = models.IntegerField(verbose_name='排序', default=0, blank=True, editable=False)

    def __unicode__(self):
        return self.spcaeTypeName

    class Meta:
        verbose_name = '空间范围'
        verbose_name_plural = verbose_name


'''
The language model
语言表
'''


class Language(models.Model):
    lanTypeName = models.CharField(max_length=50, verbose_name='类型名称', unique=True)
    sortNum = models.IntegerField(verbose_name='排序', default=0, blank=True, editable=False)

    def __unicode__(self):
        return self.lanTypeName

    class Meta:
        verbose_name = '语言'
        verbose_name_plural = verbose_name


'''
The discipline of file
文件学科表
'''


class Discipline(models.Model):
    disciplineTypeName = models.CharField(max_length=50, verbose_name='类型名称', unique=True)
    sortNum = models.IntegerField(verbose_name='排序', default=0, blank=True, editable=False)

    def __unicode__(self):
        return self.disciplineTypeName

    class Meta:
        verbose_name = '学科类型'
        verbose_name_plural = verbose_name


'''
The format of files
格式表
'''


class Format(models.Model):
    formatTypeName = models.CharField(max_length=50, verbose_name='类型名称', unique=True)
    sortNum = models.IntegerField(verbose_name='排序', default=0, blank=True, editable=False)

    def __unicode__(self):
        return self.formatTypeName

    class Meta:
        verbose_name = '格式类型'
        verbose_name_plural = verbose_name


'''
The Category model
分类属性表
'''


class Category(models.Model):
    leftNum = models.IntegerField(blank=True, default=0, null=True)
    rightNum = models.IntegerField(blank=True, null=True, default=0)
    pid = models.ForeignKey('self', blank=True, null=True, related_name='children')
    path = models.CharField(max_length=100, blank=True, null=True)
    attrName = models.CharField(max_length=50, verbose_name='属性名称')
    sortNum = models.IntegerField(verbose_name='排序', default=0)

    def __unicode__(self):
        return self.attrName

    class Meta:
        verbose_name = '分类属性'
        verbose_name_plural = verbose_name


'''
The subject model
文献专题库
'''

class Subject(models.Model):
    subjectName = models.CharField(max_length=100, verbose_name='专题名称')
    subjectDescribe = models.TextField(verbose_name='专题描述', max_length=100, help_text='最多输入100字')
    subjectPic = models.ImageField(upload_to='himalaya/images', verbose_name='缩略图')
    subjectDate = models.DateField(auto_now=True, verbose_name='创建时间')
    subVisible = models.BooleanField(verbose_name='是否可见', default=True, blank=True)
    hasChild = models.BooleanField(verbose_name='是否有子专题', default=False, blank=True)
    subParent = models.ForeignKey('self', blank=True, null=True, related_name='Parent', editable=False,
                                  verbose_name='文献子专题')

    def __unicode__(self):
        return self.subjectName

    class Meta:
        verbose_name = '文献专题'
        verbose_name_plural = verbose_name


'''
Theme of subject
专题文献属性库
'''


class SubjectTheme(models.Model):
    # TYPE_CHOICE
    fieldName = models.CharField(max_length=50, verbose_name='属性名称')
    fieldType = models.CharField(max_length=50, verbose_name='属性类型')
    isPrompt = models.BooleanField(verbose_name='是否提示')
    promtInfo = models.CharField(max_length=100, verbose_name='提示信息', blank=True, null=True)
    isMust = models.BooleanField(verbose_name='是否必填')
    corrAttri = models.IntegerField(verbose_name='关联分类属性', blank=True, null=True)
    subjectId = models.ForeignKey(Subject, verbose_name='所属专题')

    def __unicode__(self):
        return self.fieldName

    class Meta:
        verbose_name = '专题文献属性'
        verbose_name_plural = verbose_name


'''
Basic properties of file
文献基础属性库
'''


class FileBaseInfo(models.Model):
    reindex_related = ('language',)
    filecode = models.CharField(max_length=30, verbose_name='文献编号', blank=True, null=True)
    title = models.CharField(max_length=5000, verbose_name='文献名称', blank=True, null=True)
    creator = models.CharField(max_length=1000, verbose_name='作者/编者', blank=True, null=True)
    keywords = models.CharField(max_length=1000, verbose_name='关键词', help_text='关键词请用分号（；）隔开', blank=True, null=True)
    description = models.TextField(verbose_name='内容简介', blank=True, null=True)
    publisher = models.CharField(max_length=200, verbose_name='来源', blank=True, null=True)

    fileType = models.ManyToManyField(FileType, verbose_name='文件类型', help_text='多选按Ctril键', blank=True, null=True)
    language = models.ManyToManyField(Language, verbose_name='语  言', help_text='多选按Ctril键', blank=True, null=True)
    discipline = models.ManyToManyField(Discipline, verbose_name='学  科', help_text='多选按Ctril键', blank=True, null=True)
    spatial = models.ManyToManyField(SpaceScope, verbose_name='空间范围', help_text='多选按Ctril键', blank=True, null=True)
    fileFormat = models.ManyToManyField(Format, verbose_name='格式', help_text='多选按Ctril键', blank=True, null=True)

    contributor = models.CharField(max_length=200, verbose_name='译者/校订者', blank=True, null=True)
    size = models.CharField(max_length=30, verbose_name='文件大小', blank=True, editable=False, default=30, null=True)
    pubDate = models.DateField(verbose_name='出版时间', editable=False, blank=True, null=True)
    contentLength = models.IntegerField(verbose_name='页数', default=0, blank=True, null=True)
    uploadPeople = models.CharField(max_length=50, verbose_name='文件上传人', blank=True, null=True)
    uploadDate = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    updateDate = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')
    picture = models.ImageField(upload_to='himalaya/images', verbose_name='缩略图', blank=True, null=True)
    attachment = models.FileField(upload_to='himalaya/files', verbose_name='附  件', blank=True, null=True)
    notes = models.CharField(max_length=200, verbose_name='备注', blank=True, null=True)
    check = models.BooleanField(max_length=1, verbose_name='是否审核', default=True, blank=True)
    subjecttype = models.IntegerField(default=-1, verbose_name='专题类型', editable=False)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = '文献基础属性'
        verbose_name_plural = verbose_name


'''
File extends properties
专题文献库
'''


class FileExtendInfo(models.Model):
    fileId = models.IntegerField(verbose_name='文献编号', editable=False)
    fieldId = models.IntegerField(verbose_name='文献属性编号', editable=False)
    filedValue = models.CharField(max_length=1000, verbose_name='属性值', blank=True, null=True)

    def __unicode__(self):
        return self.filedValue

    class Meta:
        verbose_name = '专题文献库'
        verbose_name_plural = verbose_name


'''
VIEW
全景库
'''


class View(models.Model):
    viewName = models.CharField(max_length=100, verbose_name='全景名称')
    createDate = models.DateField(auto_now=False, verbose_name='拍摄日期')
    viewIntro = models.TextField(verbose_name='简  介', max_length=100, help_text='最多输入100字')
    viewPic = models.ImageField(upload_to='himalaya/images', verbose_name='缩略图')
    viewAuth = models.CharField(max_length=100, verbose_name='拍  摄')
    viewPlace = models.CharField(max_length=100, verbose_name='地  点')
    viewEqu = models.CharField(max_length=200, verbose_name='制  作')
    viewPath = models.FileField(upload_to='himalaya/quanjing', verbose_name='文件路径')

    def __unicode__(self):
        return self.viewName

    class Meta:
        verbose_name = '全景'
        verbose_name_plural = verbose_name


# class Termfrequency(models.Model):
# 	word = models.CharField(max_length=100)
# 	docnum = models.IntegerField(editable=False)
# 	wordnum = models.IntegerField(editable=False)
# 	docrelate = models.ManyToManyField(FileBaseInfo,blank=True)
#
# 	def __unicode__(self):
# 		return self.word


'''
书目列表
'''


class BookList(models.Model):
    bookID = models.CharField(verbose_name='书目ID', max_length=30, help_text='书目ID,中文游记以1开头,自1001开始;外文游记以2开头,以2001开始',primary_key=True)
    author = models.CharField(verbose_name='作者', max_length=1000, help_text='书目作者', blank=True, null=True)
    nationality = models.CharField(verbose_name='作者国别', max_length=1000, help_text='作者国别', blank=True, null=True)
    bNameCH = models.CharField(verbose_name='著作名称（CH）', max_length=1000, help_text='著作中文名称', blank=True, null=True)
    bNameEN = models.CharField(verbose_name='著作名称（EN）', max_length=1000, help_text='著作英文名称', blank=True, null=True)
    translator = models.CharField(verbose_name='译者', max_length=1000, help_text='译者姓名', blank=True, null=True)
    press = models.CharField(verbose_name='出版社', max_length=2000, help_text='著作出版社', blank=True, null=True)
    pubdate = models.CharField(verbose_name='出版时间', help_text='出版日期', max_length=1000, blank=True, null=True)
    Publication = models.CharField(verbose_name='刊物/汇编', max_length=1000, help_text='游记刊登刊物', blank=True, null=True)
    dopub = models.CharField(verbose_name='刊物日期', max_length=1000, help_text='刊登期刊日期', blank=True, null=True)
    notes = models.TextField(verbose_name='题解', help_text='概述作者游历原因', blank=True, null=True)
    remark = models.TextField(verbose_name='备注', blank=True, null=True)
    inputTime = models.DateField(verbose_name='录入时间', auto_now_add=True)
    pageNum = models.CharField(verbose_name='所在刊物/汇编页码', help_text='所在刊物的页码', null=True, blank=True, max_length=1000)
    Pubvolume = models.CharField(verbose_name='刊物卷期', help_text='所在刊物卷期', null=True, max_length=1000, blank=True)
    inputUser = models.CharField(verbose_name='录入人', max_length=1000, blank=True, null=True)

    def __unicode__(self):
        return self.bookID

    class Meta:
        verbose_name = '书目列表'
        verbose_name_plural = verbose_name


'''
线路
'''


class Route(models.Model):
    RouteName = models.CharField(verbose_name='线路名称', max_length=1000, null=True)
    RoutePer = models.CharField(verbose_name='游历人', max_length=1000, null=True)
    bookID = models.ForeignKey(BookList, verbose_name='书目ID')
    remark = models.TextField(verbose_name='题解', blank=True, null=True)

    def __unicode__(self):
        return self.RouteName

    class Meta:
        verbose_name = '游历线路'
        verbose_name_plural = verbose_name


'''
地点
'''


class Site(models.Model):
    sitenameCH = models.CharField(verbose_name='地点', max_length=1000, null=True)
    sitenameEN = models.CharField(verbose_name='英文/拼音', max_length=1000, blank=True, null=True)
    longitude = models.DecimalField(verbose_name='经度', max_digits=10, decimal_places=6, null=True)
    latitude = models.DecimalField(verbose_name='纬度', max_digits=10, decimal_places=6, null=True)
    altitude = models.DecimalField(verbose_name='海拔', max_digits=10, decimal_places=6, blank=True, null=True)
    region = models.ForeignKey(Category, verbose_name='所属行政区', blank=False)

    def __unicode__(self):
        return self.sitenameCH

    class Meta:
        verbose_name = '地点信息'
        verbose_name_plural = verbose_name


'''
游历点数据
'''


class TravelData(models.Model):
    siteid = models.ForeignKey(Site, verbose_name='地点', blank=False)
    RouteName = models.ForeignKey(Route, verbose_name='线路', blank=False)
    toa = models.DateField(verbose_name='到达时间', blank=True, null=True)
    tol = models.DateField(verbose_name='离开时间', blank=True, null=True)
    transportation = models.CharField(verbose_name='交通方式', help_text='游历者的交通方式：火车、轮船、马、步行等', max_length=1000,blank=True, null=True)
    nation = models.TextField(verbose_name='游历地民族', help_text='人口、民族等情况', blank=True, null=True)
    police = models.TextField(verbose_name='游历地治安', help_text='政治、军事、治安等情况', blank=True, null=True)
    economy = models.TextField(verbose_name='游历地经济', help_text='经济贸易、矿产、集市等情况', blank=True, null=True)
    agriculture = models.TextField(verbose_name='游历地农业', help_text='农业情况', blank=True, null=True)
    custom = models.TextField(verbose_name='风俗文化', help_text='婚丧礼仪、工艺文化、装饰文化、饮食文化、节日文化、戏曲文化、歌舞文化、绘画文化、音乐文化、制作文化等',blank=True, null=True)
    religion = models.TextField(verbose_name='宗教', help_text='宗教信仰情况、宗教政策、寺庙和教堂、宗教艺术等', blank=True, null=True)
    history = models.TextField(verbose_name='历史', help_text='游历者听闻的游历地历史发展情况、大的历史事件（如改土归流等）、遗迹遗址、碑刻等', blank=True,null=True)
    education = models.TextField(verbose_name='游历地教育', help_text='学校、儿童入学等教育情况', blank=True, null=True)
    geography = models.TextField(verbose_name='自然地理', help_text='自然地理、风景、自然灾害情况', blank=True, null=True)
    other = models.TextField(verbose_name='其他', help_text='其他重要信息', blank=True, null=True)
    inputTime = models.DateField(verbose_name='录入时间', auto_now_add=True)
    DataPage = models.CharField(verbose_name='数据页码', help_text='信息所在的页码', max_length=100, blank=True, null=True)
    mileage = models.CharField(verbose_name='里程', help_text='', max_length=100, blank=True, null=True)
    order = models.IntegerField(verbose_name='序列号', blank=True, null=True)
    inputUser = models.CharField(verbose_name='录入人', max_length=1000, blank=True, null=True)

    def __unicode__(self):
        content = self.siteid
        return content.sitenameCH

    class Meta:
        verbose_name = '游历点数据'
        verbose_name_plural = verbose_name


'''
游历地图片
'''


class Travelgraph(models.Model):
    graph = models.ImageField(upload_to='himalaya/travelgraph', blank=True, null=True)
    traverData = models.ForeignKey(TravelData)

    def __unicode__(self):
        return self.id

    class Meta:
        verbose_name = '游历地图片'
        verbose_name_plural = verbose_name

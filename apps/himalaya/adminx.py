#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import print_function

from xadmin.views import ModelFormAdminView

"""
Topic: xadminx定制类
Desc :
"""
# -*- coding: utf-8 -*-
import xadmin
import xadmin.views as xviews

from .models import *
from django.contrib.auth.models import User
from xadmin.layout import Fieldset
from xadmin.views import ListAdminView
from RelatePlugin import BookmarkPlugin1,RelateMenuPlugin,CreateSub,AgeListFilter
from .actions import DeleteAdminView,DeleteSelectedAction
from django.utils.translation import ugettext_lazy as _
from actions import export_as_csv_action

class BaseSetting(object):
    enable_themes = False
    use_bootswatch = False
    reversion_menu = False


xadmin.sites.site.register(xviews.BaseAdminView, BaseSetting)


class AdminSettings(object):
    # 设置base_site.html的Title
    site_title = '喜马拉雅数据库'
    # 设置base_site.html的Footer
    site_footer = 'SiChuan University'
    menu_style = 'accordion'
    hidden_menu = True

    # 菜单设置
    def get_site_menu(self):
        return (

            {'title': '首页', 'icon': 'fa fa-laptop'
                , 'url': '/xadmin'},

            {'title': '用户管理', 'icon': 'fa fa-list-ol'
                , 'url': self.get_model_url(User, 'changelist')},

            {'title': '基础数据管理', 'icon': 'fa fa-list-ol', 'perm': self.get_model_perm(FileType, 'change'), 'menus': (
                {'title': '文件类型设置', 'icon': 'fa fa-link'
                    , 'url': self.get_model_url(FileType, 'changelist')},
                {'title': '空间范围设置', 'icon': 'fa fa-link'
                    , 'url': self.get_model_url(SpaceScope, 'changelist')},
                {'title': '语言类型设置', 'icon': 'fa fa-link'
                    , 'url': self.get_model_url(Language, 'changelist')},
                {'title': '文件学科设置', 'icon': 'fa fa-link'
                    , 'url': self.get_model_url(Discipline, 'changelist')},
                {'title': '文件格式设置', 'icon': 'fa fa-link'
                    , 'url': self.get_model_url(Format, 'changelist')},
                {'title': '专题枚举数据', 'icon': 'fa fa-link'
                    , 'url': self.get_model_url(Category, 'changelist')},

            )},
            {
                'title': '游历数据管理', 'icon': 'fa fa-list-ol', 'perm': self.get_model_perm(FileType, 'change'), 'menus': (
                {'title': '书目列表管理', 'icon': 'fa fa-link'
                    , 'url': self.get_model_url(BookList, 'changelist')},
                {'title': '游历地点管理', 'icon': 'fa fa-link'
                    , 'url': self.get_model_url(Site, 'changelist')},
                {'title': '游历线路管理', 'icon': 'fa fa-link'
                    , 'url': self.get_model_url(Route, 'changelist')},
            )
            },
            {'title': '其他管理', 'icon': 'fa fa-list-ol', 'perm': self.get_model_perm(FileType, 'change'), 'menus': (
                {'title': '专题项目管理', 'icon': 'fa fa-link'
                    , 'url': self.get_model_url(Subject, 'changelist')},
                {'title': '文献资源管理', 'icon': 'fa fa-link'
                 # , 'url': '/hima/filebaseinfo.html'},
                    , 'url': self.get_model_url(FileBaseInfo, 'changelist')},
                {'title': '全景资源管理', 'icon': 'fa fa-link'
                    , 'url': self.get_model_url(View, 'changelist')},
            )}

        )





'''文件类型表'''

class FileTypeFormAdmin(object):
    # 自动编号
    actions = [DeleteSelectedAction]

    def get_account_state(self, obj):
        if (self.show_all and self.can_show_all) or not self.multi_page:
            self.page_num = 0
        return (self.page_num) * self.list_per_page + list(self.result_list).index(obj)+1

    get_account_state.short_description = u'编号'

    # 详情方法
    def getdetail(self, obj):
        return ''

    getdetail.short_description = u'详情'

    # 是否删除

    # 表的显示列
    list_display = ('get_account_state', 'fileTypeName', 'getdetail')

    search_fields = ('fileTypeName')
    style_fields = {'hosts': 'checkbox-inline'}

    # 信息详情i
    show_detail_fields = ['getdetail']
    list_per_page = 5
    ordering = ['fileTypeName']
    use_related_menu = False
    list_display_links = ('fileTypeName',)
    # remove不可以添加删除更新
    # remove_permissions = ('delete', 'add', 'update')


'''空间范围表'''
class SpaceScopeAdmin(object):
    actions = [DeleteSelectedAction]
    # fields = ['spcaeTypeName',]
    # 自动编号

    def get_account_state(self, obj):
        if (self.show_all and self.can_show_all) or not self.multi_page:
            self.page_num = 0
        return (self.page_num) * self.list_per_page + list(self.result_list).index(obj)+1

    get_account_state.short_description = u'编号'

    # 详情方法
    def getdetail(self, obj):
        return ''

    getdetail.short_description = u'详情'

    # 表的显示列
    list_display = ('get_account_state', 'spcaeTypeName', 'getdetail')
    search_fields = ('spcaeTypeName')
    # 信息详情i
    show_detail_fields = ['getdetail']
    # 每页显示多少数据
    list_per_page = 5
    # 设置是否关联属性
    list_select_related = False
    ordering = ['spcaeTypeName']
    # 相关表的最后一列去掉
    use_related_menu = False
    list_display_links = ('spcaeTypeName',)



'''语言表'''

class LanguageAdmin(object):
    actions = [DeleteSelectedAction]
    # fields = ['lanTypeName']
    # 自动编号


    def get_account_state(self, obj):
        if (self.show_all and self.can_show_all) or not self.multi_page:
            self.page_num = 0
        return (self.page_num) * self.list_per_page + list(self.result_list).index(obj)+1

    get_account_state.short_description = u'编号'

    # 详情方法
    def getdetail(self, obj):
        return ''

    getdetail.short_description = u'详情'

    # 表的显示列
    list_display = ('get_account_state', 'lanTypeName', 'getdetail')
    search_fields = ('lanTypeName',)
    # 信息详情i
    show_detail_fields = ['getdetail']
    # 每页显示多少数据
    list_per_page = 5
    ordering = ['lanTypeName']
    # 相关表的最后一列去掉
    use_related_menu = False
    list_display_links = ('lanTypeName',)



'''文件学科表'''
class DisciplineAdmin(object):
    actions = [DeleteSelectedAction]

    def get_account_state(self, obj):
        if (self.show_all and self.can_show_all) or not self.multi_page:
            self.page_num = 0
        return (self.page_num) * self.list_per_page + list(self.result_list).index(obj)+1

    get_account_state.short_description = u'编号'

    # 详情方法
    def getdetail(self, obj):
        return ''

    getdetail.short_description = u'详情'

    list_display = ('get_account_state', 'disciplineTypeName', 'getdetail')
    search_fields = ('disciplineTypeName',)
    # 信息详情i
    show_detail_fields = ['getdetail']
    # 每页显示多少数据
    list_per_page = 5
    ordering = ['disciplineTypeName']
    # 相关表的最后一列去掉
    use_related_menu = False
    list_display_links = ('disciplineTypeName',)



'''格式表'''

class FormatAdmin(object):
    actions = [DeleteSelectedAction]
    # fields = ['formatTypeName']

    # 自动编号
    def get_account_state(self, obj):
        if (self.show_all and self.can_show_all) or not self.multi_page:
            self.page_num = 0
        return (self.page_num) * self.list_per_page + list(self.result_list).index(obj)+1

    get_account_state.short_description = u'编号'

    # 详情方法
    def getdetail(self, obj):
        return ''

    getdetail.short_description = u'详情'

    # 表的显示列
    list_display = ('get_account_state', 'formatTypeName', 'getdetail')
    search_fields = ('formatTypeName',)
    # 信息详情i
    show_detail_fields = ['getdetail']
    # 每页显示多少数据
    list_per_page = 5
    ordering = ['formatTypeName']
    # 相关表的最后一列去掉
    use_related_menu = False
    list_display_links = ('formatTypeName',)

'''分类属性表'''
class CategoryAdmin(object):
    pass


class SubjectAdmin(object):
    # 自动编号

    def get_account_state(self, obj):
        if (self.show_all and self.can_show_all) or not self.multi_page:
            self.page_num = 0
        return (self.page_num) * self.list_per_page + list(self.result_list).index(obj)+1

    relatemenu = True
    createsub = True

    use_related_menu = False
    list_display = ('get_account_state', 'subjectName', 'subjectDescribe', 'subjectDate')
    get_account_state.short_description = u'编号'

    # 表的显示列
    search_fields = ('subjectName',)
    # 信息详情i
    show_detail_fields = ['subjectName']
    # 每页显示多少数据
    list_per_page = 5
    ordering = ['subjectName', 'subjectDescribe', 'subjectDate']
    list_display_links = ('subjectName',)
    reversion_enable = False





'''文献主题属性库'''
class SubjectThemeAdmin(object):
    # 自动编号

    def get_account_state(self, obj):
        if (self.show_all and self.can_show_all) or not self.multi_page:
            self.page_num = 0
        return (self.page_num) * self.list_per_page + list(self.result_list).index(obj)+1

    get_account_state.short_description = u'编号'


    #关联分类属性树形显示字符串
    def get_attrname(self, obj):
        # obj.fildId是fileextendinfo的对应文献基础信息表filebaseinfo的id
        if ((int(obj.fieldType) == 5) or (int(obj.fieldType) == 6)):
            return Category.objects.get(id=int(obj.corrAttri))
        else:
            return ''

    get_attrname.short_description = u'关联分类属性'

    def get_filetype(self, obj):
        if ((int(obj.fieldType) == 0)):
            return '字符串类型'
        if ((int(obj.fieldType) == 1)):
            return '整型'
        if ((int(obj.fieldType) == 2)):
            return '实数型'
        if ((int(obj.fieldType) == 3)):
            return '日期类型'
        if ((int(obj.fieldType) == 4)):
            return '布尔类型'
        if ((int(obj.fieldType) == 5) or (int(obj.fieldType) == 6)):
            return '枚举类型'

    get_filetype.short_description = u'属性类别'
    # 表的显示列




    def get_attrname(self, obj):
        # obj.fildId是fileextendinfo的对应文献基础信息表filebaseinfo的id
        if ((int(obj.fieldType) == 5) or (int(obj.fieldType) == 6)):
            return Category.objects.get(id=int(obj.corrAttri))
        else:
            return ''

    get_attrname.short_description = u'关联分类属性'


    def get_sujectname(self, obj):
        return Subject.objects.get(id=int(obj.subjectId_id)).subjectName
    get_sujectname.short_description = u'所属专题名称'



    list_display = ( 'fieldName', 'get_filetype', 'isPrompt', 'promtInfo', 'isMust', 'get_attrname','get_sujectname')
    search_fields = ('fieldName',)
    # 每页显示多少数据
    list_per_page = 5
    ordering = ['fieldName']
    list_display_links = ('fieldName',)
    hidden_menu = True



def getchild(it):
    child = []
    child.append(it.id)
    if it.hasChild:
        for item in Subject.objects.filter(subParent=it):
            child+=getchild(item)
    return child



'''文献基础属性库'''
class FileBaseInfoAdmin(object):
    actions = [DeleteSelectedAction]
    # 自动编号

    def get_account_state(self, obj):
        if (self.show_all and self.can_show_all) or not self.multi_page:
            self.page_num = 0
        return (self.page_num) * self.list_per_page + list(self.result_list).index(obj)+1

    get_account_state.short_description = u'编号'

    # 显示专题名称
    def get_subjecttitle(self, obj):
        # obj.fildId是fileextendinfo的对应文献基础信息表filebaseinfo的id
        if (obj.subjecttype == -1):
            return u'基础文献'
        else:
            res = Subject.objects.get(id=obj.subjecttype)
            return res.subjectName

    get_subjecttitle.short_description = u'专题名称'
    get_subjecttitle.allow_tags = True
    get_subjecttitle.is_column = True

    #chubanshijian
    def get_year(self, obj):
        # obj.fildId是fileextendinfo的对应文献基础信息表filebaseinfo的id
        if(obj.pubDate==None):
            return '空'
        else:
            return str(obj.pubDate)[0:4]+'年'

    get_year.short_description = u'出版时间'
    get_year.allow_tags = True
    get_year.is_column = True


    # 表的显示列
    list_display = ('get_account_state', 'title', 'creator', 'publisher', 'get_year', 'uploadDate', 'updateDate', 'get_subjecttitle')

    list_display_links = ('title',)
    # search_fields = ('title',)
    # 信息详情i
    show_detail_fields = ('title')
    search_fields = ('filecode','title', 'creator', 'publisher', 'keywords', 'description', 'uploadPeople')
    # 每页显示多少数据
    list_per_page = 40
    list_max_show_all = 50



    #filte
    rest = Subject.objects.all()
    ss = [{'title':"基础文献",
           'query':{'subjecttype':-1},
           'cols': ('get_account_state', 'title', 'creator', 'publisher', 'get_year', 'uploadDate', 'updateDate', 'get_subjecttitle'),
           }]
    for it in rest:
        child = getchild(it)
        # result = dict()
        # for i,item in enumerate(child):
        #     result['subjecttype_%s' % i] = item
        temp = {'title':it.subjectName,
                'query':{'subjecttype':it.id},
                'cols': ('get_account_state', 'title', 'creator', 'publisher', 'get_year', 'uploadDate', 'updateDate', 'get_subjecttitle')}
        ss.append(temp)
    show_bookmarks = False
    menu_title = u"专题类型"

    # choices_subjecttitle = [
    #     (0, 'male'),
    #     (1, 'femal'),
    # ]
    #
    # list_filter = choices_subjecttitle
    selfmark = True
    list_bookmarks = ss
    Fieldset.widget = 100
    ordering = ['-updateDate']


'''全景'''
class ViewAdmin(object):
    actions = [DeleteSelectedAction]
    # 自动编号


    def get_account_state(self, obj):
        if (self.show_all and self.can_show_all) or not self.multi_page:
            self.page_num = 0
        return (self.page_num) * self.list_per_page + list(self.result_list).index(obj)+1

    get_account_state.short_description = u'编号'

    # 表的显示列

    list_display = ('get_account_state', 'viewName', 'createDate', 'viewAuth', 'viewEqu','viewPlace')
    search_fields = ('viewName',)
    # 信息详情i
    show_detail_fields = ['viewName']
    # 每页显示多少数据
    list_per_page = 5
    ordering = ['viewName', 'createDate', 'viewAuth', 'viewPlace']
    list_display_links = ('viewName',)


class FileExtendInfoAdmain(object):
    # 自动编号


    def get_account_state(self, obj):
        if (self.show_all and self.can_show_all) or not self.multi_page:
            self.page_num = 0
        return (self.page_num) * self.list_per_page + list(self.result_list).index(obj)+1

    get_account_state.short_description = u'编号'

    # 显示基础文献title
    def get_filebasetitle(self, obj):
        # obj.fildId是fileextendinfo的对应文献基础信息表filebaseinfo的id
        res = FileBaseInfo.objects.get(id=obj.fileId)
        return res.title

    get_filebasetitle.short_description = u'文献名称'

    # 显示对应的专题title
    def get_sujecttitle(self, obj):
        # obj.fildId是fileextendinfo的对应文献基础信息表filebaseinfo的id
        res = FileBaseInfo.objects.get(id=obj.fileId)
        subres = Subject.objects.get(id=res.subjecttype)
        return subres.subjectName

    get_sujecttitle.short_description = u'对应专题名称'

    # 显示对应的属性名称
    def get_atrrname(self, obj):
        # obj.fildId是fileextendinfo的对应文献基础信息表filebaseinfo的id
        res = SubjectTheme.objects.get(id=obj.fieldId)
        return res.fieldName

    get_atrrname.short_description = u'属性名称'

    # 表的显示列
    list_display = ('get_account_state', 'get_filebasetitle', 'get_sujecttitle', 'get_atrrname', 'filedValue',)
    search_fields = ('filedValue',)
    # 信息详情i
    show_detail_fields = ['filedValue']
    # 每页显示多少数据
    list_per_page = 5
    ordering = ['fileId']
    hidden_menu = True  # 设置不显示此模块菜单
    reversion_enable = False

class BookListAdmin(object):
    def getdetail(self, obj):
        return ''

    getdetail.short_description = u'详情'

    list_display = ('bookID','author', 'nationality','bNameCH','bNameEN','translator','press','pubdate','Publication','dopub','pageNum','Pubvolume','inputTime')
    search_fields = ('bookID','author','nationality','bNameCH','bNameEN','translator','press')
    # 信息详情i
    show_detail_fields = ['bookID']
    # 每页显示多少数据
    list_per_page = 5
    ordering = ['bookID']
    # 相关表的最后一列去掉
    use_related_menu = False
    list_display_links = ('bookID')




class RouteAdmin(object):
    def get_account_state(self, obj):
        if (self.show_all and self.can_show_all) or not self.multi_page:
            self.page_num = 0
        return (self.page_num) * self.list_per_page + list(self.result_list).index(obj)+1

    def getdetail(self, obj):
        return ''

    def get_bookID(self,obj):
        item = obj.bookID
        return  item.bNameCH + '/' + item.author

    get_account_state.short_description = u'编号'
    getdetail.short_description = u'详情'
    get_bookID.short_description = u'引用书目'

    Route_allow = True
    list_display = ('get_account_state', 'RouteName', 'RoutePer', 'get_bookID')
    search_fields = ('RouteName', 'RoutePer')
    # 信息详情i
    show_detail_fields = ['RouteName']
    # 每页显示多少数据
    list_per_page = 5
    actions = [export_as_csv_action("导出 CSV", fields=['RouteName'])]
    # 相关表的最后一列去掉
    #use_related_menu = False
    list_display_links = ('RouteName')
    list_export = ()


class TravelDataAdmin(object):
    hidden_menu = True

    def getsite(self,obj):
        return obj.siteid

    getsite.short_description = u'地点'
    list_display =('order','getsite','toa','tol','transportation','DataPage')
    search_fields = ('getsite','transportation','DataPage')
    show_detail_fields=['order']
    list_editable=['order']
    ordering=['order']
    list_per_page = 5
    # 相关表的最后一列去掉
    use_related_menu = False
    list_display_links = ('getsite')



class SiteAdmin(object):
    # 自动编号
    def get_account_state(self, obj):
        if (self.show_all and self.can_show_all) or not self.multi_page:
            self.page_num = 0
        return (self.page_num) * self.list_per_page + list(self.result_list).index(obj)+1

    def getdetail(self, obj):
        return ''

    def get_region(self, obj):
        return obj.region

    get_account_state.short_description = u'编号'
    getdetail.short_description = u'详情'
    get_region.short_description=u'所属行政区'

    list_display = ('get_account_state','sitenameCH', 'sitenameEN','get_region')
    search_fields = ('sitenameCH', 'sitenameEN')
    # 信息详情i
    show_detail_fields = ['sitenameCH']
    # 每页显示多少数据
    list_per_page = 5
    # 相关表的最后一列去掉
    use_related_menu = False
    list_display_links = ('sitenameCH')



xadmin.site.register(xviews.DeleteAdminView,DeleteAdminView)
xadmin.site.register_plugin(BookmarkPlugin1, ListAdminView)
xadmin.site.register_plugin(RelateMenuPlugin,ListAdminView)
# xadmin.site.register_plugin(SelfFilterPlugin, ListAdminView)
xadmin.site.register_plugin(CreateSub,ModelFormAdminView)


xadmin.site.register_modelview(r'^list$', ListAdminView, name='%s_%s_list')

xadmin.site.register(xviews.CommAdminView, AdminSettings)
xadmin.site.register(FileType, FileTypeFormAdmin)
xadmin.site.register(SpaceScope, SpaceScopeAdmin)
xadmin.site.register(Language, LanguageAdmin)
xadmin.site.register(Discipline, DisciplineAdmin)
xadmin.site.register(Format, FormatAdmin)
xadmin.site.register(Category, CategoryAdmin)
xadmin.site.register(Subject, SubjectAdmin)
xadmin.site.register(SubjectTheme, SubjectThemeAdmin)
xadmin.site.register(FileBaseInfo, FileBaseInfoAdmin)
xadmin.site.register(FileExtendInfo, FileExtendInfoAdmain)
xadmin.site.register(View, ViewAdmin)
xadmin.site.register(BookList,BookListAdmin)
xadmin.site.register(Route,RouteAdmin)
xadmin.site.register(Site,SiteAdmin)
xadmin.site.register(TravelData,TravelDataAdmin)
# xadmin.site.register(SubJournal,SubJournalAdmin)
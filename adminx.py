#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: xadminx定制类
Desc :
"""
# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
import xadmin
import xadmin.views as xviews
from .models import *
from django.contrib.auth.models import User
from django import forms
from xadmin.layout import Main, TabHolder, Tab, Fieldset, Row, Col, AppendedText, Side
from django.utils.datastructures import OrderedDict
from django.utils.text import capfirst
import os,shutil
import json, copy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, MultiField, Div, Field
from xadmin.views import BaseAdminView
from xadmin.views import BaseAdminView, CommAdminView, ListAdminView

from django.core.exceptions import PermissionDenied
from django.db import transaction, router
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.contrib.admin.utils import get_deleted_objects

from xadmin.util import unquote,model_ngettext
from xadmin.views.edit import UpdateAdminView
from xadmin.views.detail import DetailAdminView
from xadmin.views.base import ModelAdminView, filter_hook, csrf_protect_m
from xadmin.plugins.actions import BaseActionView

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
            {'title': '其他管理', 'icon': 'fa fa-list-ol', 'perm': self.get_model_perm(FileType, 'change'), 'menus': (
                {'title': '专题项目管理', 'icon': 'fa fa-link'
                    , 'url': self.get_model_url(Subject, 'changelist')},
                {'title': '文献资源管理', 'icon': 'fa fa-link'
                 # , 'url': '/hima/filebaseinfo.html'},
                    , 'url': self.get_model_url(FileBaseInfo, 'changelist')},
                {'title': '全景资源管理', 'icon': 'fa fa-link'
                    , 'url': self.get_model_url(View, 'changelist')},

                # {'title': '专题扩展属性', 'icon': 'fa fa-link'
                #  # , 'url': '/hima/ceshi.html'},
                #     , 'url': self.get_model_url(SubjectTheme, 'changelist')},

            )}

        )



ACTION_CHECKBOX_NAME = '_selected_action'
class DeleteSelectedAction(BaseActionView):

    action_name = "delete_selected"
    description = _(u'Delete selected %(verbose_name_plural)s')

    delete_confirmation_template = None
    delete_selected_confirmation_template = None

    delete_models_batch = True

    model_perm = 'delete'
    icon = 'fa fa-times'

    @filter_hook
    def delete_models(self, queryset):
        n = queryset.count()
        print 22222
        if n:
            if self.delete_models_batch:
                for data in queryset:
                    for field in data._meta.fields:
                        s = getattr(data,field.name)
                        if(os.path.isfile('./media/'+str(s))==True):
                            if(str(s).find("/quanjing/")==-1):
                                os.remove('./media/' + str(s))
                            else:
                                s = str(s).split("/")
                                str1 = s[0:3]
                                str1 = '/'.join(str1)
                                shutil.rmtree('./media/'+str1)
                                os.remove('./media/'+str1+'.zip')
                queryset.delete()
            else:
                for obj in queryset:
                    for field in obj._meta.fields:
                        s = getattr(obj, field.name)
                        if (os.path.isfile('./media/' + str(s)) == True):
                            if (str(s).find("/quanjing/") == -1):
                                os.remove('./media/' + str(s))
                            else:
                                s = str(s).split("/")
                                str1 = s[0:3]
                                str1 = '/'.join(str1)
                                shutil.rmtree('./media/' + str1)
                                os.remove('./media/' + str1 + '.zip')
                    obj.delete()
            self.message_user(_("Successfully deleted %(count)d %(items)s.") % {
                "count": n, "items": model_ngettext(self.opts, n)
            }, 'success')

    @filter_hook
    def do_action(self, queryset):
        # Check that the user has delete permission for the actual model
        if not self.has_delete_permission():
            raise PermissionDenied

        using = router.db_for_write(self.model)

        # Populate deletable_objects, a data structure of all related objects that
        # will also be deleted.
        deletable_objects, model_count, perms_needed, protected = get_deleted_objects(
            queryset, self.opts, self.user, self.admin_site, using)

        # The user has already confirmed the deletion.
        # Do the deletion and return a None to display the change list view again.
        if self.request.POST.get('post'):
            if perms_needed:
                raise PermissionDenied
            self.delete_models(queryset)
            # Return None to display the change list page again.
            return None

        if len(queryset) == 1:
            objects_name = force_unicode(self.opts.verbose_name)
        else:
            objects_name = force_unicode(self.opts.verbose_name_plural)

        if perms_needed or protected:
            title = _("Cannot delete %(name)s") % {"name": objects_name}
        else:
            title = _("Are you sure?")

        context = self.get_context()
        context.update({
            "title": title,
            "objects_name": objects_name,
            "deletable_objects": [deletable_objects],
            'queryset': queryset,
            "perms_lacking": perms_needed,
            "protected": protected,
            "opts": self.opts,
            "app_label": self.app_label,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
        })

        # Display the confirmation page
        return TemplateResponse(self.request, self.delete_selected_confirmation_template or
                                self.get_template_list('views/model_delete_selected_confirm.html'), context, current_app=self.admin_site.name)

'''文件类型表'''

filetypei = 0
filetypelen = 0
filetypedata = len(FileType.objects.all())
filetypebl = False
filetyperesult=0

class FileTypeFormAdmin(object):
    # 自动编号

    def get_account_state(self, obj):
        global filetypelen,filetyperesult
        # filetypelen=self.page_num
        global filetypei, filetypedata
        global filetypebl
        # filetypelen=0
        if ((len(self.result_list) == len(FileType.objects.all()))):
            if (filetypebl == False or (filetypei >= len(FileType.objects.all()))):
                filetypebl = True
                filetypei = 0
            filetypei += 1
            return filetypei
        elif ((self.page_num != filetypelen) or (filetypei >= self.list_per_page) or (
                    filetypei >= len(FileType.objects.all())) or (filetypedata != len(FileType.objects.all())) or (
            filetypei >= (filetypedata - (self.page_num) * self.list_per_page)) or (filetyperesult!=len(self.result_list))):
            filetyperesult = len(self.result_list)
            filetypei = 0
            filetypelen = self.page_num
            filetypedata = len(FileType.objects.all())
        filetypei += 1
        filetypebl = False
        return (self.page_num) * self.list_per_page + filetypei

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

spacescopei = 0
spacescopelen = 0
spacescopedata = len(SpaceScope.objects.all())
spacescopebl = False
spaceresult=0

class SpaceScopeAdmin(object):
    # fields = ['spcaeTypeName',]
    # 自动编号

    def get_account_state(self, obj):
        global spacescopelen,spaceresult
        # filetypelen=self.page_num
        global spacescopei, spacescopedata, spacescopebl
        if ((len(self.result_list) == len(SpaceScope.objects.all()))):
            if (spacescopebl == False or (spacescopei >= len(SpaceScope.objects.all()))):
                spacescopebl = True
                spacescopei = 0
            spacescopei += 1
            return spacescopei
        elif ((self.page_num != spacescopelen) or (spacescopei >= self.list_per_page) or (
                    spacescopei >= len(SpaceScope.objects.all())) or (
            spacescopedata != len(SpaceScope.objects.all())) or (
            spacescopei >= (spacescopedata - (self.page_num) * self.list_per_page)) or (spaceresult!=len(self.result_list))):
            spaceresult = len(self.result_list)
            spacescopei = 0
            spacescopelen = self.page_num
            spacescopedata = len(SpaceScope.objects.all())
        spacescopei += 1
        spacescopebl = False
        return (self.page_num) * self.list_per_page + spacescopei

    get_account_state.short_description = u'编号'

    # 详情方法
    def getdetail(self, obj):
        return ''

    getdetail.short_description = u'详情'

    # 表的显示列
    fieldsets = [
        (None, {'fields': ['spcaeTypeName']}),
    ]
    list_display = ('get_account_state', 'spcaeTypeName', 'getdetail')
    search_fields = ('spaceTypeName',)
    # 信息详情i
    show_detail_fields = ['getdetail']
    # 每页显示多少数据
    list_per_page = 5
    # 设置是否关联属性
    list_select_related = False
    ordering = ['spcaeTypeName']
    # 相关表的最后一列去掉
    use_related_menu = False
    fields=['spcaeTypeName']
    list_display_links = ('spcaeTypeName',)



'''语言表'''

languagei = 0
languagelen = 0
languagedata = len(Language.objects.all())
languagebl = False
languageresult=0

class LanguageAdmin(object):
    # fields = ['lanTypeName']
    # 自动编号


    def get_account_state(self, obj):
        global languagei,languageresult
        global languagelen, languagedata, languagebl
        if ((len(self.result_list) == len(Language.objects.all()))):
            if (languagebl == False or (languagei >= len(Language.objects.all()))):
                languagebl = True
                languagei = 0
            languagei += 1
            return languagei
        elif ((self.page_num != languagelen) or (languagei >= self.list_per_page) or (
                    languagei >= len(Language.objects.all())) or (languagedata != len(Language.objects.all())) or (
            languagei >= (languagedata - (self.page_num) * self.list_per_page)) or (languageresult!=len(self.result_list))):
            languageresult = len(self.result_list)
            languagei = 0
            languagelen = self.page_num
            languagedata = len(Language.objects.all())
        languagei += 1
        languagebl = False
        return (self.page_num) * self.list_per_page + languagei

    get_account_state.short_description = u'编号'

    # 详情方法
    def getdetail(self, obj):
        return ''

    getdetail.short_description = u'详情'

    # 表的显示列

    fieldsets = [
        (None, {'fields': ['lanTypeName']}),
        ('排序', {'fields': ['sortNum'], 'classes': ['collapse']}),
    ]
    list_display = ('get_account_state', 'lanTypeName', 'getdetail')
    search_fields = ('lanTypeName',)
    # 信息详情i
    show_detail_fields = ['getdetail']
    # 每页显示多少数据
    list_per_page = 5
    ordering = ['lanTypeName']
    # 相关表的最后一列去掉
    use_related_menu = False
    fields=['id','lanTypeName']
    list_display_links = ('lanTypeName',)



'''文件学科表'''
disciplinei = 0
disciplinelen = 0
disciplinedata = len(Discipline.objects.all())
disciplinebl = False
disciplineresult=0

class DisciplineAdmin(object):
    # fields = ['disciplineTypeName']
    # 自动编号
    global disciplinei
    disciplinei = 0

    def get_account_state(self, obj):
        global disciplinei,disciplineresult
        global disciplinelen, disciplinedata, disciplinebl
        if ((len(self.result_list) == len(Discipline.objects.all()))):
            if (disciplinebl == False or (disciplinei >= len(Discipline.objects.all()))):
                disciplinebl = True
                disciplinei = 0
            disciplinei += 1
            return disciplinei
        elif ((self.page_num != disciplinelen) or (disciplinei >= self.list_per_page) or (
                    disciplinei >= len(Discipline.objects.all())) or (
            disciplinedata != len(Discipline.objects.all())) or (
            disciplinei >= (disciplinedata - (self.page_num) * self.list_per_page)) or(disciplineresult!=(len(self.result_list)))):
            disciplineresult = len(self.result_list)
            disciplinei = 0
            disciplinelen = self.page_num
            disciplinedata = len(Discipline.objects.all())
        disciplinei += 1
        disciplinebl = False
        return (self.page_num) * self.list_per_page + disciplinei

    get_account_state.short_description = u'编号'

    # 详情方法
    def getdetail(self, obj):
        return ''

    getdetail.short_description = u'详情'

    # 表的显示列


    fieldsets = [
        (None, {'fields': ['disciplineTypeName']}),
        ('排序', {'fields': ['sortNum'], 'classes': ['collapse']}),
    ]
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
formatei = 0
formalen = 0
formatedata = len(Format.objects.all())
formatebl = False
formatresult=0

class FormatAdmin(object):
    # fields = ['formatTypeName']

    # 自动编号
    global formatei
    formatei = 0

    def get_account_state(self, obj):
        global formatei,formatresult
        global formalen, formatedata, formatebl
        if ((len(self.result_list) == len(Format.objects.all()))):
            if (formatebl == False or (formatei >= len(Format.objects.all()))):
                formatebl = True
                formatei = 0
            formatei += 1
            return formatei
        if ((self.page_num != formalen) or (formatei >= self.list_per_page) or (
            formatei >= len(Format.objects.all())) or (formatedata != len(Format.objects.all()))
            or (formatei >= (formatedata - (self.page_num) * self.list_per_page)) or (formatresult!=len(self.result_list))):
            formatresult = len(self.result_list)
            formatei = 0
            formalen = self.page_num
            formatedata = len(Format.objects.all())
        formatei += 1
        formatebl = False
        return (self.page_num) * self.list_per_page + formatei

    get_account_state.short_description = u'编号'

    # 详情方法
    def getdetail(self, obj):
        return ''

    getdetail.short_description = u'详情'

    # 表的显示列


    fieldsets = [
        (None, {'fields': ['formatTypeName']}),
        ('排序', {'fields': ['sortNum'], 'classes': ['collapse']}),
    ]
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
categoryi = 0
categorylen = 0
categorydata = len(Category.objects.all())
categorybl = False


class CategoryAdmin(object):
    # 自动编号
    global categoryi
    categoryi = 0

    def get_account_state(self, obj):
        global categoryi
        global categorylen, categorydata, categorybl
        if ((len(self.result_list) == len(Category.objects.all()))):
            if (categorybl == False or (categoryi >= len(Category.objects.all()))):
                categorybl = True
                categoryi = 0
            categoryi += 1
            return categoryi
        elif ((self.page_num != categorylen) or (categoryi >= self.list_per_page) or (
                    categoryi >= len(Category.objects.all())) or (categorydata != len(Category.objects.all())) or (
            categoryi >= (categorydata - (self.page_num) * self.list_per_page))):
            categoryi = 0
            categorylen = self.page_num
            categorydata = len(Category.objects.all())
        categoryi += 1
        categorybl = False
        return (self.page_num) * self.list_per_page + categoryi

    get_account_state.short_description = u'编号'

    # 表的显示列

    list_display = ('get_account_state', 'leftNum', 'rightNum', 'pid', 'path', 'attrName')
    search_fields = ('attrName',)
    # 信息详情i
    show_detail_fields = ['attrName']
    # 每页显示多少数据
    list_per_page = 5
    ordering = ['attrName']
    # 相关表的最后一列去掉
    use_related_menu = False


'''文献专题库'''
subjecti = 0
subjectlen = 0
subjectdata = len(Subject.objects.all())
subjectbl = False
subjectresult=0

class SubjectAdmin(object):
    # 自动编号
    global subjecti
    subjecti = 0

    def get_account_state(self, obj):
        global subjecti,subjectresult
        global subjectlen, subjectdata, subjectbl
        if ((len(self.result_list) == len(Subject.objects.all()))):
            if (subjectbl == False or (subjecti >= len(Subject.objects.all()))):
                subjectbl = True
                subjecti = 0
            subjecti += 1
            return subjecti
        elif ((self.page_num != subjectlen) or (subjecti >= self.list_per_page) or (
                    subjecti >= len(Subject.objects.all())) or (subjectdata != len(Subject.objects.all())) or (
            subjecti >= (subjectdata - (self.page_num) * self.list_per_page)) or (subjectresult!=len(self.result_list))):
            subjectresult = len(self.result_list)
            subjecti = 0
            subjectlen = self.page_num
            subjectdata = len(Subject.objects.all())

        subjecti += 1
        subjectbl = False
        return (self.page_num) * self.list_per_page + subjecti

    get_account_state.short_description = u'编号'

    # 表的显示列

    list_display = ('get_account_state', 'subjectName', 'subjectDescribe', 'subjectDate')
    search_fields = ('subjectName',)
    # 信息详情i
    show_detail_fields = ['subjectName']
    # 每页显示多少数据
    list_per_page = 5
    ordering = ['subjectName', 'subjectDescribe', 'subjectDate']
    list_display_links = ('subjectName',)



'''文献主题属性库'''
subjectthemei = 0
subjectthemelen = 0
subjectthemedata = len(SubjectTheme.objects.all())
subjectthemebl = False
subjectthemeresult=0

class SubjectThemeAdmin(object):
    # 自动编号
    global subjectthemei
    subjectthemei = 0

    def get_account_state(self, obj):
        global subjectthemei,subjectthemeresult
        global subjectthemelen, subjectthemedata, subjectthemebl
        if ((len(self.result_list) == len(SubjectTheme.objects.all()))):
            if (subjectthemebl == False or (subjectthemei >= len(SubjectTheme.objects.all()))):
                subjectthemebl = True
                subjectthemei = 0
            subjectthemei += 1
            return subjectthemei
        elif ((self.page_num != subjectthemelen) or (subjectthemei >= self.list_per_page) or (
                    subjectthemei >= len(SubjectTheme.objects.all())) or (
            subjectthemedata != len(SubjectTheme.objects.all()))
              or (subjectthemei >= (subjectthemedata - (self.page_num) * self.list_per_page)) or (subjectthemeresult!=len(self.result_list))):
            subjectthemeresult= len(self.result_list)
            subjectthemei = 0
            subjectthemelen = self.page_num
            subjectthemedata = len(SubjectTheme.objects.all())
        subjectthemei += 1
        subjectthemebl = False
        return (self.page_num) * self.list_per_page + subjectthemei

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


'''文献基础属性库'''
filebaseinfoi = 0
filebaseinfolen = 0
filebaseinfodata = len(FileBaseInfo.objects.all())
filebaseinfobl = False
filebaseinforesult=0

class FileBaseInfoAdmin(object):
    actions = [DeleteSelectedAction]
    # 自动编号
    global filebaseinfoi
    filebaseinfoi = 0
    print 'filebaseinfoi',filebaseinfoi
    def get_account_state(self, obj):
        print '搜索结果条数：',len(self.result_list)

        global filebaseinfoi,filebaseinforesult
        global filebaseinfolen, filebaseinfodata, filebaseinfobl

        if ((len(self.result_list) == len(FileBaseInfo.objects.all()))):
            if (filebaseinfobl == False or (filebaseinfoi >= len(FileBaseInfo.objects.all()))):
                filebaseinfobl = True
                filebaseinfoi = 0
            filebaseinfoi += 1
            return filebaseinfoi
        if ((self.page_num != filebaseinfolen) or (filebaseinfoi >= self.list_per_page) or (
                    filebaseinfoi >= len(FileBaseInfo.objects.all())) or (
            filebaseinfodata != len(FileBaseInfo.objects.all()))
            or (filebaseinfoi >= (filebaseinfodata - (self.page_num) * self.list_per_page)) or (filebaseinforesult !=len(self.result_list))):

            filebaseinforesult=len(self.result_list)

            filebaseinfoi = 0
            filebaseinfolen = self.page_num
            filebaseinfodata = len(FileBaseInfo.objects.all())
        filebaseinfoi += 1
        filebaseinfobl = False
        return (self.page_num) * self.list_per_page + filebaseinfoi

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
    list_per_page = 5
    # ordering = ['get_subjecttitle']
    Fieldset.widget = 100
    ordering = ['-updateDate']

'''全景'''
viewid = 0
viewlen = 0
viewdata = len(View.objects.all())
viewbl = False
viewresult=0

class ViewAdmin(object):
    actions = [DeleteSelectedAction]
    # 自动编号


    def get_account_state(self, obj):
        global viewid,viewresult
        global viewlen, viewdata, viewbl
        if ((len(self.result_list) == len(View.objects.all()))):
            if (viewbl == False or (viewid >= len(View.objects.all()))):
                viewbl = True
                viewid = 0
            viewid += 1
            return viewid
        elif ((self.page_num != viewlen) or (viewid >= self.list_per_page) or (viewid >= len(View.objects.all())) or (
            viewdata != len(View.objects.all()))
              or (viewid >= (viewdata - (self.page_num) * self.list_per_page)) or (viewresult!=len(self.result_list))):
            viewresult = len(self.result_list)
            viewid = 0
            viewlen = self.page_num
            viewdata = len(View.objects.all())
        viewid += 1
        viewbl = False
        return (self.page_num) * self.list_per_page + viewid

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



fxiid = 0
fxilen = 0
fxidata = len(FileExtendInfo.objects.all())
fxibl = False


class FileExtendInfoAdmain(object):
    # 自动编号


    def get_account_state(self, obj):
        global fxiid
        global fxilen, fxidata, fxibl
        if ((len(self.result_list) == len(FileExtendInfo.objects.all()))):
            if (fxibl == False or (fxiid >= len(FileExtendInfo.objects.all()))):
                fxibl = True
                fxiid = 0
            fxiid += 1
            return fxiid
        elif ((self.page_num != fxilen) or (fxiid >= self.list_per_page) or (
            fxiid >= len(FileExtendInfo.objects.all())) or (
                    fxidata != len(FileExtendInfo.objects.all()))
              or (fxiid >= (fxidata - (self.page_num) * self.list_per_page))):
            fxiid = 0
            fxilen = self.page_num
            fxidata = len(FileExtendInfo.objects.all())
        fxiid += 1
        fxibl = False
        return (self.page_num) * self.list_per_page + fxiid

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







class DeleteAdminView(xviews.DeleteAdminView):
    delete_confirmation_template = None

    def init_request(self, object_id, *args, **kwargs):
        "The 'delete' admin view for this model."
        self.obj = self.get_object(unquote(object_id))

        if not self.has_delete_permission(self.obj):
            raise PermissionDenied

        if self.obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(self.opts.verbose_name), 'key': escape(object_id)})

        using = router.db_for_write(self.model)

        # Populate deleted_objects, a data structure of all related objects that
        # will also be deleted.
        (self.deleted_objects, model_count, self.perms_needed, self.protected) = get_deleted_objects(
            [self.obj], self.opts, self.request.user, self.admin_site, using)

    @csrf_protect_m
    @filter_hook
    def get(self, request, object_id):
        context = self.get_context()
        print 'ooooo',len(self.deleted_objects)
        return TemplateResponse(request, self.delete_confirmation_template or
                                self.get_template_list("views/model_delete_confirm.html"), context, current_app=self.admin_site.name)

    @csrf_protect_m
    @transaction.atomic
    @filter_hook
    def post(self, request, object_id):
        if self.perms_needed:
            raise PermissionDenied

        self.delete_model()

        response = self.post_response()
        if isinstance(response, basestring):
            return HttpResponseRedirect(response)
        else:
            return response

    @filter_hook
    def delete_model(self):
        """
        Given a model instance delete it from the database.
        """
        self.obj.delete()

    @filter_hook
    def get_context(self):
        if self.perms_needed or self.protected:
            title = _("Cannot delete %(name)s") % {"name":
                                                   force_unicode(self.opts.verbose_name)}
        else:
            title = _("Are you sure?")

        print 'ooooo',len(self.deleted_objects)

        new_context = {
            "title": title,
            "object": self.obj,
            "deleted_objects": self.deleted_objects,
            "perms_lacking": self.perms_needed,
            "protected": self.protected,
        }
        context = super(DeleteAdminView, self).get_context()
        context.update(new_context)
        return context

    @filter_hook
    def get_breadcrumb(self):
        bcs = super(DeleteAdminView, self).get_breadcrumb()
        bcs.append({
            'title': force_unicode(self.obj),
            'url': self.get_object_url(self.obj)
        })
        item = {'title': _('Delete')}
        if self.has_delete_permission():
            item['url'] = self.model_admin_url('delete', self.obj.pk)
        bcs.append(item)

        return bcs

    @filter_hook
    def post_response(self):

        self.message_user(_('The %(name)s "%(obj)s" was deleted successfully.') %
                          {'name': force_unicode(self.opts.verbose_name), 'obj': force_unicode(self.obj)}, 'success')

        if not self.has_view_permission():
            return self.get_admin_url('index')
        return self.model_admin_url('changelist')





xadmin.site.register(xviews.DeleteAdminView,DeleteAdminView)



xadmin.site.register_modelview(r'^list$', ListAdminView, name='%s_%s_list')

xadmin.site.register(xviews.CommAdminView, AdminSettings)
# xadmin.site.register(xviews.MyAdminView,AdminSettings)
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

# update_index
# import apps.himalaya.search_indexes
# from haystack.management.commands import update_index
# #
# update_index.Command().handle()

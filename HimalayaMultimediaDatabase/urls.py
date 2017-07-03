# coding=utf-8
"""HimalayaMultimediaDatabase URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

import xadmin

xadmin.autodiscover()

from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from apps.himalaya.xadmin_views import *

urlpatterns = [
	# 显示自己的页面
	# 基础文献的添加
	url(r'^xadmin/himalaya/filebaseinfo/filebaseinfoadd/(?P<dynamicsubjectid>\d+)/$',filebaseinfoadd),
	# 修改文献添加button
	url(r'^xadmin/himalaya/filebaseinfo/add/$',filechoiceadd),
	# 添加文献主题属性库
	url(r'^xadmin/himalaya/filebaseinfo/subjectinfoadd/(?P<dynamicfilebaseid>\d+)/$',sujectinfoadd),
	# 文献的编辑
	url(r'^xadmin/himalaya/filebaseinfo/(?P<id>\d+)/update/$',filebaseinfoedit),
	url(r'^xadmin/himalaya/fileextendinfo/(?P<id>\d+)/update/$', fileextendinfoedit),
	# 文献详情显示
	url(r'^xadmin/himalaya/filebaseinfo/(?P<id>\d+)/detail/$', filebasedetail),
	# view添加，实现文件解压
	url(r'^xadmin/himalaya/view/add/$', viewadd),
	# view修改页面，实现文件解压
	url(r'^xadmin/himalaya/view/(?P<id>\d+)/update/$', viewedite),
	#url(r'^admin/', include(admin.site.urls)),
	url(r'^xadmin/himalaya/filebaseinfo/swfupload/(?P<dynamicfilebaseid>\d+)/$', swfupload),
    url(r'^xadmin/himalaya/filebaseinfo/swfmodify/$', swfmodify),
	url(r'^xadmin/himalaya/filebaseinfo/swfchoice/$', swfchoice),
	url(r'^xadmin/himalaya/swfaddr/$', swfaddr),
	url(r'^xadmin/himalaya/modifyaddr/$', modifyaddr),
	#laotang
	#laotang
	url(r'^xadmin/himalaya/category/(?P<id>\d+)/update/$', tree_update),
	url(r'^xadmin/himalaya/subjecttheme/(?P<id>\d+)/update/$', subjecttheme_update),
	url(r'^xadmin/himalaya/category/$', category),
	url(r'^xadmin/himalaya/category/add/$', category),
	url(r'^xadmin/himalaya/test/$', test),
	url(r'^xadmin/himalaya/subjecttheme_category/$', subjecttheme_category),
	url(r'^xadmin/himalaya/Category_data_upload/$', Category_data_upload),
	url(r'^xadmin/himalaya/subjecttheme/add/$', subjecttheme_add),
	url(r'^xadmin/himalaya/route/add/$',Routeadd),
	url(r'^xadmin/himalaya/route/(?P<id>\d+)/update/$',Routeupdate),

	url(r'^xadmin/himalaya/traveldata/$',travelist),
	url(r'^xadmin/himalaya/traveldata/add/$',traveladd),
	url(r'^xadmin/himalaya/traveldata/(?P<id>\d+)/update/$',travelupdate),
	url(r'^xadmin/himalaya/traveldata/(?P<id>\d+)/detail/$',traveldetail),

	url(r'^xadmin/himalaya/site/add/$',siteadd),
	url(r'^xadmin/himalaya/site/(?P<id>\d+)/update/$',siteupdate),

	url(r'^xadmin/himalaya/site/gis_location',gis_location),

	url(r'^xadmin/himalaya/test/$',test),
	# 文献扩展的编辑
	# url(r'^xadmin/himalaya/fileextendinfo/(?P<id>\d+)/update/$', 'apps.himalaya.xadmin_views.fileextendinfoedit'),
	# # 文献详情显示
	# url(r'^xadmin/himalaya/filebaseinfo/(?P<id>\d+)/detail/$', 'apps.himalaya.xadmin_views.filebasedetail'),
	# # view添加，实现文件解压
	# url(r'^xadmin/himalaya/view/add/$', 'apps.himalaya.xadmin_views.viewadd'),
	# # view修改页面，实现文件解压
	# url(r'^xadmin/himalaya/view/(?P<id>\d+)/update/$', 'apps.himalaya.xadmin_views.viewedite'),
	# #url(r'^admin/', include(admin.site.urls)),
	# url(r'^xadmin/himalaya/filebaseinfo/swfupload/(?P<dynamicfilebaseid>\d+)/$', 'apps.himalaya.xadmin_views.swfupload'),
    # url(r'^xadmin/himalaya/filebaseinfo/swfmodify/$', 'apps.himalaya.xadmin_views.swfmodify'),
	# url(r'^xadmin/himalaya/filebaseinfo/swfchoice/$', 'apps.himalaya.xadmin_views.swfchoice'),
	# url(r'^xadmin/himalaya/swfaddr/$', 'apps.himalaya.xadmin_views.swfaddr'),
	# url(r'^xadmin/himalaya/modifyaddr/$', 'apps.himalaya.xadmin_views.modifyaddr'),
	# #laotang
	# #laotang
	# url(r'^xadmin/himalaya/category/(?P<id>\d+)/update/$', 'apps.himalaya.xadmin_views.tree_update'),
	# url(r'^xadmin/himalaya/subjecttheme/(?P<id>\d+)/update/$', 'apps.himalaya.xadmin_views.subjecttheme_update'),
	# url(r'^xadmin/himalaya/category/$', 'apps.himalaya.xadmin_views.category'),
	# url(r'^xadmin/himalaya/test/$', 'apps.himalaya.xadmin_views.test'),
	# url(r'^xadmin/himalaya/subjecttheme_category/$', 'apps.himalaya.xadmin_views.subjecttheme_category'),
	# url(r'^xadmin/himalaya/Category_data_upload/$', 'apps.himalaya.xadmin_views.Category_data_upload'),
	# url(r'^xadmin/himalaya/subjecttheme/add/$', 'apps.himalaya.xadmin_views.subjecttheme_add'),
	url(r'xadmin/', include(xadmin.site.urls)),
	# url(r'^search/', include('haystack.urls')),
	# url(r'', include('apps.himadatabase.urls', namespace='hima')),
	url(r'^media/(?P<path>.*)$', django.views.static.serve,
             {'document_root': settings.MEDIA_ROOT}),
	url(r'', include('apps.himalaya.urls', namespace='himalaya')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


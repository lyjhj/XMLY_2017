# coding=utf-8
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static


from . import views
from . import location

urlpatterns = [
                  url(r'^$', views.home, name='home'),
                  url(r'^panorama/', views.panorama, name='panorama'),
                  url(r'^show/$', views.show, name='show'),
                  url(r'^detail/(?P<pk_id>\d+)/$', views.detail, name='detail'),
                  url(r'^specialist/$', views.specialist, name='specialist'),

                  url(r'^subject/', views.search_subject, name='search-sub'),
                  url(r'^search/', views.full_search, name='search'),
                  url(r'^termfreq',views.termfreq,name='termfreq'),
                  url(r'^advanced/', views.advanced_search, name='advanced'),

                  url(r'^statisticInfo/',views.full_statistic, name='statisticInfo'),
                  url(r'^subject_statisticInfo/',views.subject_statistic, name='subject_statisticInfo'),
                  url(r'^base_statisticInfo/',views.base_statistic, name='base_statisticInfo'),

                  # url(r'^show_1/$', views.show_1, name='show_1'),
                  url(r'^base_search/$', views.base_search, name='base-search'),
                  # url(r'^redict/', views.update_url, name='url-update'),


                  #map test start
                  url(r'^example/', location.example, name='example'),
                  url(r'^position/', location.position, name='position'),
                  #map test end

                  url(r'^timerange/', location.timerange, name='timerange'),
                  url(r'^gis_show/', location.gis_show, name='gis_show'),

                  # 游历专题  start
                  url(r'^mapview/', location.mapview, name='mapview'),
                  url(r'^route_map/', location.route_map, name='route_map'),
                  # 游历专题  end
                  # url(r'^search/$', views.search, name='search'),
                  #############017-06-26
                  # url(r'^sub_specialist/', views.sub_specialist, name='sub_specialist'),
                  # url(r'^sub_keywords', views.sub_keywords, name='sub_keywords'),
                  # url(r'^sub_cluster', views.sub_cluster, name='sub_cluster'),
                  # url(r'^base_keywords', views.base_keywords, name='base_keywords'),
                  # url(r'^base_cluster', views.base_cluster, name='base_cluster'),
                  # url(r'^base_cocreator', views.base_cocreator, name="base_cocreator"),
                  # url(r'^full_keywords', views.full_keywords, name='full_keywords'),
    
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

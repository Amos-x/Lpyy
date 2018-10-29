# __author__ = "Amos"
# Email: 379833553@qq.com

from django.urls import path,re_path
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

schema_view = get_schema_view(title='Pastebin API')

urlpatterns = [
    path('schema/',schema_view),
    path('client/', views.ClientList.as_view()),
    re_path('client/(?P<pk>[0-9]+)/$', views.ClientDetail.as_view()),
    path('project/', views.ProjectList.as_view()),
    re_path('^project/(?P<pk>[0-9]+)/$', views.ProjectDetail.as_view()),
    path('project/deploy/', views.ProjectDeploy.as_view()),
    re_path('clientinfo/', views.ClientInfo.as_view()),
    path('crontab/', views.CrontabList.as_view()),
    re_path('crontab/(?P<pk>[0-9]+)/$', views.CrontabDetail.as_view()),
    path('interval/', views.IntervalList.as_view()),
    re_path('interval/(?P<pk>[0-9]+)/$', views.IntervalDetail.as_view()),
    path('task/', views.PeriodicTaskList.as_view()),
    re_path('task/(?P<pk>[0-9]+)/$', views.PeriodicTaskDetail.as_view()),
    path('celerytasks/',views.CeleryTasks.as_view()),
]
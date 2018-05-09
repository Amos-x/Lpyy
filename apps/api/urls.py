# __author__ = "Amos"
# Email: 379833553@qq.com

from django.urls import path,include,re_path
from apps.api import views
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

router = DefaultRouter()

schema_view = get_schema_view(title='Pastebin API')

urlpatterns = [
    path('',include(router.urls)),
    path('schema/',schema_view),
    path('client/', views.ClientList.as_view()),
    re_path('client/(?P<pk>[0-9]+)/$', views.ClientDetail.as_view()),
    path('project/', views.ProjectList.as_view()),
    re_path('^project/(?P<pk>[0-9]+)/$', views.ProjectDetail.as_view()),
    path('project/deploy/', views.ProjectDeploy.as_view()),
    re_path('client/(?P<pk>[0-9]+)/status/$', views.client_status),
    re_path('clientinfo/', views.ClientInfo.as_view()),
    path('job/', views.Job.as_view()),
    path('job/log/', views.JobLogList.as_view()),
    path('task/', views.TaskList.as_view()),
    re_path('task/(?P<pk>[0-9]+)/$', views.TaskDetail.as_view()),
    path('task/switch/', views.task_switch),
    # path('task/email/',views.EmailScheduler.as_view()),
]
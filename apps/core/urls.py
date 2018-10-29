# __author__ = "Amos"
# Email: 379833553@qq.com

from django.urls import path,re_path
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from django.conf.urls.static import static
from django.conf import settings

schema_view = get_schema_view(title='Pastebin API')

urlpatterns = [
    re_path('job/log/(?P<c>[0-9]+)/(?P<p>.+)/(?P<s>.+)/(?P<j>.+)/',views.joblog),
    path('index/', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('userinfo/', views.user_profile, name='userinfo'),
    path('userinfo/change_passwd', views.change_password, name='change_password'),
    path('userinfo/change_email', views.change_email, name='change_email'),
    re_path('userinfo/reset_email/(?P<user_id>[0-9]+)/(?P<reset_code>[a-zA-Z0-9]+)/$', views.reset_email, name='reset_email'),
    re_path('userinfo/reset_passwd/(?P<reset_code>[a-zA-Z0-9]+)/$', views.reset_password,name='reset_password'),
    path('userinfo/edit', views.edit_userinfo, name='edit_userinfo'),
    path('userinfo/uploadimg', views.upload_img, name='upload_img'),
    path('settings/', views.settings, name='settings'),
    path('logout/', views.logout, name='logout'),
    path('forgot/', views.forgot_password, name='forgot_password'),
    path('client/', views.client_index, name='client_index'),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

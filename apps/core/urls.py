# __author__ = "Amos"
# Email: 379833553@qq.com

from django.urls import path,re_path
from core import views

urlpatterns = [
    re_path('job/log/(?P<c>[0-9]+)/(?P<p>.+)/(?P<s>.+)/(?P<j>.+)/',views.joblog),
]
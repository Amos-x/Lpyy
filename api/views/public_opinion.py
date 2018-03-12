# __author__ = "Amos"
# Email: 379833553@qq.com
from rest_framework import viewsets
from core import models
from api import serializers
import logging



class CustomerViewset(viewsets.ModelViewSet):
    queryset = models.Customer.objects.all()
    serializer_class = serializers.CustomerSerializers


# Keyword 的models是需要修改的，修改后可能会改变视图
class KeywordViewset(viewsets.ModelViewSet):
    queryset = models.Keyword.objects.all()
    serializer_class = serializers.KeywordSerializers


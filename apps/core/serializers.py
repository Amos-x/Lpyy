# __author__ = "Amos"
# Email: 379833553@qq.com

from rest_framework import serializers
from . import models
from django_celery_beat.models import CrontabSchedule,IntervalSchedule,PeriodicTask


class ClientSimpleInfoSerializers(serializers.ModelSerializer):

    class Meta:
        model = models.Client
        fields = ('id','name')


class ProjectSimpleInfoSerializers(serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = ('id','name')


# class DjangoJobSimpleInfoSerializers(serializers.ModelSerializer):
#
#     class Meta:
#         model = models.DjangoJob
#         fields = ('id','name')


class DeploySimpleInfoSerializers(serializers.ModelSerializer):
    client = ClientSimpleInfoSerializers(read_only=True)
    project = ProjectSimpleInfoSerializers(read_only=True)

    class Meta:
        model = models.Deploy
        fields = ('client','project','description','deployed_at')


class ClientSerializers(serializers.ModelSerializer):

    class Meta:
        model = models.Client
        fields = ('id','name','ip','port','description','auth','username','password','status')


class ProjectSerializers(serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = ('id','name','description','egg','built_at')


class DeploySerializers(serializers.ModelSerializer):

    class Meta:
        model = models.Deploy
        fields = ('id','client','project','description','deployed_at')


class ProDepSerializers(serializers.ModelSerializer):
    pro_deploy = DeploySimpleInfoSerializers(many=True,read_only=True)

    class Meta:
        model = models.Project
        fields = ('id','name','description','egg','built_at','pro_deploy')


class CrontabScheduleSerializers(serializers.ModelSerializer):

    class Meta:
        model = CrontabSchedule
        fields = ('id','minute','hour','day_of_week','day_of_month','month_of_year')


class IntervalScheduleSerializers(serializers.ModelSerializer):

    class Meta:
        model = IntervalSchedule
        fields = ('id','every','period')


class PeriodicTaskSerializers(serializers.ModelSerializer):
    interval = IntervalScheduleSerializers(read_only=True)
    crontab = CrontabScheduleSerializers(read_only=True)

    class Meta:
        model = PeriodicTask
        fields = ('id','name','task','interval','crontab','kwargs','description')

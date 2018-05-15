# __author__ = "Amos"
# Email: 379833553@qq.com

from rest_framework import serializers
from core import models


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
        fields = ('id','name','ip','port','description','auth','username','password')


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


# class TaskSerializers(serializers.ModelSerializer):
#     client = ClientSimpleInfoSerializers(read_only=True)
#     project = ProjectSimpleInfoSerializers(read_only=True)
#
#     class Meta:
#         model = models.Task
#         fields = ('client','project','spiders','crontab','is_active','created_at','updated_at')
#
#
# class DjangoJobSerializers(serializers.ModelSerializer):
#     jobinfo = TaskSerializers(read_only=True)
#
#     class Meta:
#         model = models.DjangoJob
#         fields = ('id','name','next_run_time','jobinfo')
#
#
# class JobLogSerializers(serializers.ModelSerializer):
#     client = ClientSimpleInfoSerializers(read_only=True)
#     project = ProjectSimpleInfoSerializers(read_only=True)
#     task = DjangoJobSimpleInfoSerializers(read_only=True)
#
#     class Meta:
#         model = models.ScrapydJobLog
#         fields = ('id','client','project','spider','job','task','created_at')

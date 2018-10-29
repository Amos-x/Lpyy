# __author__ = "Amos"
# Email: 379833553@qq.com

from django.http import Http404
from django.conf import settings
from django.utils import timezone
import os,pytz,time,requests,json
from ..build import find_egg,build_project
from .. import utils
from core import models
from .. import serializers
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
import shutil


class ClientList(APIView):

    def get(self,request,format=None):
        """
        get client list
        """
        queryset = models.Client.objects.all()
        p = PageNumberPagination()
        page = p.paginate_queryset(queryset=queryset, request=request, view=self)
        s = serializers.ClientSerializers(page, many=True)
        return p.get_paginated_response(s.data)

    def post(self,request,format=None):
        """
        create a client
        """
        s = serializers.ClientSerializers(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientDetail(APIView):

    def get_object(self,pk):
        try:
            return models.Client.objects.get(pk=pk)
        except models.Client.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        client = self.get_object(pk)
        s = serializers.ClientSerializers(client)
        return Response(s.data)

    def put(self, request, pk, format=None):
        client = self.get_object(pk)
        s = serializers.ClientSerializers(client, data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        client = self.get_object(pk)
        if client.cli_tasks.all():
            return Response({'status':"error","message":"此client被使用于调度任务中，无法删除"})
        client.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectList(APIView):

    def get(self,request,format=None):
        """ List all project """
        path = utils.get_project_path()
        files = os.listdir(path)
        project_list = []
        for file in files:
            project_path = os.path.join(path,file)
            if os.path.isdir(project_path) and not file in settings.IGNORES:
                project_list.append({'name':file})
                egg = find_egg(project_path)
                if egg:
                    if not models.Project.objects.filter(name=file):
                        built_at = timezone.datetime.fromtimestamp(os.path.getmtime(os.path.join(project_path, egg)),
                                                                   tz=pytz.timezone(settings.TIME_ZONE))
                        models.Project(name=file, built_at=built_at, egg=egg).save()
                else:
                    if not models.Project.objects.filter(name=file):
                        models.Project(name=file).save()
        objs = models.Project.objects.all()
        p = PageNumberPagination()
        page = p.paginate_queryset(queryset=objs,request=request, view=self)
        s = serializers.ProjectSerializers(page, many=True)
        return p.get_paginated_response(s.data)


class ProjectDetail(APIView):

    def get_object(self,pk):
        try:
            return models.Project.objects.get(pk=pk)
        except models.Project.DoesNotExist:
            raise Http404

    def get(self,request,pk,format=None):
        """ get detail project"""
        obj = self.get_object(pk)
        s = serializers.ProjectSerializers(obj)
        return Response(s.data)

    def put(self,request,pk,format=None):
        """
        build project create egg file
        need: description
        """
        obj = self.get_object(pk)
        project_path = utils.get_project_path(obj.name)
        build_project(obj.name)
        egg = find_egg(project_path)
        if not egg:
            return Response({'message': 'create egg file error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        obj.built_at = timezone.now()
        obj.egg = egg
        s = serializers.ProjectSerializers(obj, data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk,format=None):
        """ delete project """
        obj = self.get_object(pk)
        if obj.pro_tasks.all():
            return Response({'status': "error","message": "项目被使用于调度任务中，无法删除"})
        for client in obj.pro_deploy.all():
            scrapyd = utils.get_scrapyd(client.client)
            scrapyd.delete_project(obj.name)
        project_path = utils.get_project_path(obj.name)
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectDeploy(APIView):

    def get(self,request,format=None):
        """
        project deploy info list
        need :
        proejct : proejct_id as required
        """
        params = request.query_params.dict()
        if params.get('project'):
            project_obj = models.Project.objects.filter(id=params.get('project')).first()
            if project_obj:
                s = serializers.ProDepSerializers(project_obj)
                return Response(s.data)
        return Response({"status": "error", "message": "Parameter Error"},status=status.HTTP_400_BAD_REQUEST)

    def post(self,request,format=None):
        """
        project deploy, post need:
        project : project id as required
        client : client id as required
        """
        try:
            pro_obj = models.Project.objects.get(id=request.data.get('project'))
            cli_obj = models.Client.objects.get(id=request.data.get('client'))
        except:
            return Response({"status": "error", "message": "Parameter Error"}, status=status.HTTP_400_BAD_REQUEST)
        path = os.path.join(os.path.dirname(os.getcwd()), settings.PROJECTS_FOLDER)
        project_path = os.path.join(path, pro_obj.name)
        egg = find_egg(project_path)
        if not egg:
            return Response({'message': 'egg not found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        scrapyd = utils.get_scrapyd(cli_obj)
        egg_file = open(os.path.join(project_path, egg), 'rb')
        str_time = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        scrapyd.add_version(pro_obj.name, str_time, egg_file)
        egg_file.close()
        deploy_obj = models.Deploy.objects.filter(client=cli_obj,project=pro_obj).first()
        data1 = {"deployed_at": timezone.now(), "description": pro_obj.description}
        if deploy_obj:
            data2 = dict(request.data, **data1)
            s = serializers.DeploySerializers(deploy_obj, data=data2)
        else:
            # d = {'client_id':request.data.get('client'),'project_id':request.data.get('project')}
            data2 = dict(request.data, **data1)
            s = serializers.DeploySerializers(data=data2)
        if s.is_valid():
            s.save()
            return Response(s.data,status=status.HTTP_201_CREATED)
        return Response(s.errors,status=status.HTTP_400_BAD_REQUEST)


class ClientInfo(APIView):

    def get(self,request,format=None):
        """
        get client's all projects and spiders
        need params:
        client： as required
        project_name: no required
        """
        params = request.query_params.dict()
        client = params.get('client')
        if client:
            client_obj = models.Client.objects.filter(id=client).first()
            if client_obj:
                scrapyd = utils.get_scrapyd(client_obj)
                project_name = params.get('project_name')
                projects = scrapyd.list_projects()
                if project_name:
                    if project_name in projects:
                        return Response({project_name:scrapyd.list_spiders(project_name)})
                else:
                    client_info = {}
                    for x in projects:
                        client_info[x] = scrapyd.list_spiders(x)
                    return Response(client_info)
        return Response({"status": "error", "message": "Parameter Error"},status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,format=None):
        """
        delete project from client
        need:
        client: as required
        project_name: as required
        """
        params = request.query_params.dict()
        client = params.get('client')
        if client:
            client_obj = models.Client.objects.get(id=client)
            scrapyd = utils.get_scrapyd(client_obj)
            project = params.get('project_name')
            if project:
                projects = scrapyd.list_projects()
                if project in projects:
                    scrapyd.delete_project(project)
                    return Response(status.HTTP_204_NO_CONTENT)
        return Response({"status":"error","message": "Parameter Error"},status=status.HTTP_400_BAD_REQUEST)


class EmailScheduler(APIView):

    def get(self,request,format=None):
        """
        get email-scheduler-job info
        """
        email_job = models.DjangoJob.objects.filter(name='email_scheduler').first()
        if email_job:
            job = scheduler.get_job(job_id=email_job.name)
            info = get_schedulerjob_info(job=job)
            return Response(info)
        return Response({'status': 'error','message':'email scheduler do not exist'})

    def post(self,request,format=None):
        """
        create a email-scheduler-job
        need params:
        crontab : 任务调度计划时间，crontab的校验需要前端限制一下
        """
        email_job = models.DjangoJob.objects.filter(name='email_scheduler').first()
        if not email_job:
            crontab = request.data.get('crontab')
            if not crontab:
                crontab = '00 10 * * *'
            job = scheduler.add_job(send_mass_email,CronTrigger.from_crontab(crontab),id='email_scheduler')
            info = get_schedulerjob_info(job=job)
            return Response(info,status=status.HTTP_201_CREATED)
        return Response({'status':"error","message":'email-scheduler-job is exist'},status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,format=None):
        """
        修改邮箱功能调度时间，need params：
        crrontab: 调度时间
        """
        crontab = request.data.get('crontab')
        if crontab:
            job = scheduler.reschedule_job(job_id='email_scheduler',trigger=CronTrigger.from_crontab(crontab))
            info = get_schedulerjob_info(job=job)
            return Response(info)
        return Response({"status": "error", "message": "Parameter Error"},status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,format=None):
        scheduler.remove_job(job_id='email_scheduler')
        return Response(status=status.HTTP_204_NO_CONTENT)
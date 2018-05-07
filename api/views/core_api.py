# __author__ = "Amos"
# Email: 379833553@qq.com

from django.shortcuts import render,HttpResponse
from django.http import JsonResponse,Http404
from django.conf import settings
from django.utils import timezone
from django.forms.models import model_to_dict
import os,pytz,time,requests,json
from core.build import find_egg,build_project
from core import utils
from core import models
from api import serializers
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
            return Response({'status':"error","message":"scrapyd被应用为调度任务，无法删除"})
        client.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectList(APIView):

    def get(self,request,format=None):
        """ List all project """
        path = os.path.abspath(os.path.join(os.getcwd(), settings.PROJECTS_FOLDER))
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
        s = serializers.ProjectSerializers(page,many=True)
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
        path = os.path.abspath(os.path.join(os.getcwd(), settings.PROJECTS_FOLDER))
        project_path = os.path.join(path, obj.name)
        build_project(obj.name)
        egg = find_egg(project_path)
        if not egg:
            return Response({'message': 'egg not found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        obj.built_at = timezone.now()
        obj.egg = egg
        s = serializers.ProjectSerializers(obj,data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk,format=None):
        """ delete project """
        obj = self.get_object(pk)
        if obj.pro_tasks.all():
            return Response({'status':"error","message":"项目被应用为调度任务，无法删除"})
        for client in obj.pro_deploy.all():
            scrapyd = utils.get_scrapyd(client.client)
            scrapyd.delete_project(obj.name)
        path = os.path.join(os.path.abspath(os.getcwd()), settings.PROJECTS_FOLDER)
        project_path = os.path.join(path, obj.name)
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
        path = os.path.abspath(os.path.join(os.getcwd(), settings.PROJECTS_FOLDER))
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
            s = serializers.DeploySerializers(deploy_obj,data=data2)
        else:
            # d = {'client_id':request.data.get('client'),'project_id':request.data.get('project')}
            data2 = dict(request.data, **data1)
            s = serializers.DeploySerializers(data=data2)
        if s.is_valid():
            s.save()
            return Response(s.data,status=status.HTTP_201_CREATED)
        return Response(s.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def client_status(request,pk):
    """
    get scrapy client status
    """
    if request.method == 'GET':
        client_obj = models.Client.objects.get(pk=pk)
        try:
            url = utils.scrapyd_status_url(client_obj.ip,client_obj.port)
            response = requests.get(url,timeout=2)
            return Response(json.loads(response.text))
        except:
            return Response({"status": "error","message":"Connect Error"},status=500)


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


class Job(APIView):

    def get(self,request,format=None):
        """
        get project job list
        need params:
        client: as required
        project_name: as required
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
                        result = scrapyd.list_jobs(project_name)
                        jobs = []
                        statuses = ['pending', 'running', 'finished']
                        for stat in statuses:
                            for job in result.get(stat):
                                job['status'] = stat
                                jobs.append(job)
                        return Response(jobs)
        return Response({"status":"error","message": "Parameter Error"},status=status.HTTP_400_BAD_REQUEST)

    def post(self,request,format=None):
        """
        Schedule a job to run
        need params:
        client
        project_name
        spider
        """
        client = request.data.get('client')
        if client:
            client_obj = models.Client.objects.filter(id=client).first()
            if client_obj:
                scrapyd = utils.get_scrapyd(client_obj)
                project_name = request.data.get('project_name')
                if project_name:
                    projects = scrapyd.list_projects()
                    if project_name in projects:
                        spider_name = request.data.get('spider')
                        spiders = scrapyd.list_spiders(project_name)
                        if spider_name in spiders:
                            job = scrapyd.schedule(project_name, spider_name)
                            pro_obj = models.Project.objects.filter(name=project_name).first()
                            if pro_obj:
                                job_obj = models.ScrapydJobLog(
                                    client = client_obj,
                                    project = pro_obj,
                                    spider = spider_name,
                                    job = job,
                                )
                                job_obj.save()
                                s = serializers.JobLogSerializers(job_obj)
                                return Response(s.data,status=status.HTTP_201_CREATED)
                            return Response({'job':job,'warning':'project do not exist'},status=status.HTTP_204_NO_CONTENT)
        return Response({"status":"error","message": "Parameter Error"}, status=status.HTTP_400_BAD_REQUEST)


class JobLogList(APIView):

    def get(self,request,format=None):
        params = request.query_params.dict()
        # TODO 编写根据参数进行joblog查询
        queryset = models.ScrapydJobLog.objects.all()
        p = PageNumberPagination()
        page = p.paginate_queryset(queryset=queryset, request=request, view=self)
        s = serializers.JobLogSerializers(page, many=True)
        return p.get_paginated_response(s.data)

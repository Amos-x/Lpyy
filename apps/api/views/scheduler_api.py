# __author__ = "Amos"
# Email: 379833553@qq.com

from django.http import Http404
from django.db.models import Q
from django_celery_beat import models
from celery import current_app
from .. import serializers
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class CrontabList(APIView):

    def get(self,request,format=None):
        """
        get crontab scheduler list
        """
        queryset = models.CrontabSchedule.objects.all()
        p = PageNumberPagination()
        page = p.paginate_queryset(queryset=queryset, request=request, view=self)
        s = serializers.CrontabScheduleSerializers(page, many=True)
        return p.get_paginated_response(s.data)

    def post(self,request,format=None):
        """
        create a crontab
        """
        s = serializers.CrontabScheduleSerializers(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class CrontabDetail(APIView):

    def get_object(self,pk):
        try:
            return models.CrontabSchedule.objects.get(pk=pk)
        except models.CrontabSchedule.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        crontab = self.get_object(pk)
        s = serializers.CrontabScheduleSerializers(crontab)
        return Response(s.data)

    def put(self, request, pk, format=None):
        crontab = self.get_object(pk)
        s = serializers.CrontabScheduleSerializers(crontab, data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        crontab = self.get_object(pk)
        tasks = models.PeriodicTask.objects.filter(crontab=crontab)
        if tasks:
            return Response({'status':"error","message":"此crontab被使用于调度任务中，无法删除","tasks":tasks})
        crontab.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IntervalList(APIView):

    def get(self,request,format=None):
        """
        get crontab scheduler list
        """
        queryset = models.IntervalSchedule.objects.all()
        p = PageNumberPagination()
        page = p.paginate_queryset(queryset=queryset, request=request, view=self)
        s = serializers.IntervalScheduleSerializers(page, many=True)
        return p.get_paginated_response(s.data)

    def post(self,request,format=None):
        """
        create a crontab
        """
        s = serializers.IntervalScheduleSerializers(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class IntervalDetail(APIView):

    def get_object(self,pk):
        try:
            return models.IntervalSchedule.objects.get(pk=pk)
        except models.IntervalSchedule.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        interval = self.get_object(pk)
        s = serializers.IntervalScheduleSerializers(interval)
        return Response(s.data)

    def put(self, request, pk, format=None):
        interval = self.get_object(pk)
        s = serializers.IntervalScheduleSerializers(interval, data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        interval = self.get_object(pk)
        tasks = models.PeriodicTask.objects.filter(interval=interval)
        if tasks:
            return Response({'status':"error","message":"此crontab被使用于调度任务中，无法删除","tasks":tasks})
        interval.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PeriodicTaskList(APIView):

    def get(self,request,format=None):
        """
        get PeriodicTask list
        """
        queryset = models.PeriodicTask.objects.filter(~Q(name='celery.backend_cleanup'))
        p = PageNumberPagination()
        page = p.paginate_queryset(queryset=queryset, request=request, view=self)
        s = serializers.PeriodicTaskSerializers(page, many=True)
        return p.get_paginated_response(s.data)

    def post(self,request,format=None):
        """
        create a PeriodicTask
        """
        s = serializers.PeriodicTaskSerializers(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class PeriodicTaskDetail(APIView):

    def get_object(self,pk):
        try:
            return models.PeriodicTask.objects.get(pk=pk)
        except models.PeriodicTask.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        task = self.get_object(pk)
        s = serializers.PeriodicTaskSerializers(task)
        return Response(s.data)

    def put(self, request, pk, format=None):
        task = self.get_object(pk)
        s = serializers.PeriodicTaskSerializers(task, data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        task = self.get_object(pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CeleryTasks(APIView):

    def get(self, request, format=None):
        current_app.loader.import_default_modules()
        tasks = list(name for name in current_app.tasks if not name.startswith('celery.'))
        return Response({"data": tasks})

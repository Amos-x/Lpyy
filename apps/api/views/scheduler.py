# # __author__ = "Amos"
# # Email: 379833553@qq.com
#
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.executors.pool import ThreadPoolExecutor
# from apscheduler.triggers.cron import CronTrigger
# from django_apscheduler.jobstores import DjangoJobStore,register_events
# from rest_framework.views import APIView,Response
# from rest_framework.pagination import PageNumberPagination
# from rest_framework.decorators import api_view
# from rest_framework import status
# from django.conf import settings
# from django.db.models import Q
# # from django.core.mail import send_mass_mail,BadHeaderError
# from django.forms import model_to_dict
# from django.http import Http404
# from apps.api import serializers
# from core import models
# from core.utils import get_scrapyd
# import logging
#
# logger = logging.getLogger('django')
#
# executors = {
#     'default': ThreadPoolExecutor(settings.THREAD_POOL_NUM)
# }
# job_defaults = {
#             'coalesce': True,       # 如果有几次未执行，条件可以时是否只执行一次
#             'max_instances': settings.MAX_INSTANCES,     # 同一个job同一时间最多有几个实例再跑
#         }
#
# scheduler = BackgroundScheduler(executors=executors,job_defaults=job_defaults)
# scheduler.add_jobstore(DjangoJobStore(), 'default')
# register_events(scheduler)
# # scheduler.start()
# logger.info('Scheduler started')
#
#
# # def send_mass_email():
# #     subject = '汇大舆情信息提醒'
# #     from_email = settings.DEFAULT_FROM_EMAIL
# #     to_email_user_objs = models.OaUsersInfo.objects.filter(is_send_email=True).all()
# #     info_list = []
# #     for obj in to_email_user_objs:
# #         # 这里查出未读信息，放入messgae中
# #         message = '测试用数据'
# #         mess = (subject,message,from_email,[obj.email])
# #         info_list.append(mess)
# #         try:
# #             success_num = send_mass_mail(tuple(info_list),fail_silently=False)
# #             logger.info('邮件发送成功,成功数量：%s' % success_num)
# #         except BadHeaderError:
# #             logger.error('发送邮件错误：Invalid header found')
#
#
# def spider_scheduler(client,project,spiders,name):
#     client_obj = models.Client.objects.filter(id=client).first()
#     if client_obj:
#         scrapyd = get_scrapyd(client_obj)
#         pro_obj = models.Project.objects.filter(id=project).first()
#         if pro_obj:
#             if spiders:
#                 spider_list = spiders
#             else:
#                 spider_list = scrapyd.list_spiders(project)
#             for spider in spider_list:
#                 job = scrapyd.schedule(project, spider)
#                 models.ScrapydJobLog.objects.create(
#                     client=client_obj,
#                     project=pro_obj,
#                     spider=spider,
#                     job=job,
#                     task=name,
#                 )
#
#
# class TaskList(APIView):
#
#     def get(self,request,format=None):
#         """
#         获取定时任务列表
#         """
#         tasks = models.DjangoJob.objects.filter(~Q(name='email_scheduler')).all()
#         p = PageNumberPagination()
#         page = p.paginate_queryset(queryset=tasks, request=request, view=self)
#         s = serializers.DjangoJobSerializers(page, many=True)
#         return p.get_paginated_response(s.data)
#
#     def post(self,request,format=None):
#         """
#         创建一个定时调度任务，需要传的参数如下：
#         name: job调度任务的名称。
#         client : scrapyd客户端的id
#         project：项目id
#         spiders：爬虫spider名称列表，接受 列表或None！
#         crontab: crontab格式的定时配置
#         """
#         crontab = request.data.get('crontab')
#         project_obj = models.Project.objects.filter(id=request.data.get('project')).first()
#         if project_obj:
#             try:
#                 request.data.pop('crontab')
#                 job_obj = scheduler.add_job(spider_scheduler,CronTrigger.from_crontab(crontab),id=request.data.get('name'),
#                                                 kwargs=request.data)
#                 spiders = request.data.get('spiders')
#                 djangojob_job = models.DjangoJob.objects.get(name=job_obj.id)
#                 models.Task.objects.create(
#                     name = djangojob_job,
#                     client_id = request.data.get('client'),
#                     project = project_obj,
#                     spiders = (str(spiders) if spiders else None),
#                     crontab = crontab,
#                 )
#                 s = serializers.DjangoJobSerializers(djangojob_job)
#                 return Response(s.data,status=status.HTTP_201_CREATED)
#             except Exception as e:
#                 return Response({'status':"error","message":e},status=status.HTTP_400_BAD_REQUEST)
#         return Response({"status":"error","message":"project do not exist"},status=status.HTTP_400_BAD_REQUEST)
#
#
# class TaskDetail(APIView):
#
#     def get_object(self,pk):
#         try:
#             return models.DjangoJob.objects.get(pk=pk)
#         except models.Project.DoesNotExist:
#             raise Http404
#
#     def get(self,request,pk,format=None):
#         """
#         获取单个job作业信息
#         """
#         obj = self.get_object(pk)
#         s = serializers.DjangoJobSerializers(obj)
#         return Response(s.data)
#
#     def put(self,request,pk,format=None):
#         """
#         编辑修改job作业信息，同时会修改调度器中的job作业
#         只能修改job任务的 client，project，spiders
#         """
#         obj = self.get_object(pk)
#         if 'crontab' in request.data.keys():
#             request.data.pop('crontab')
#         request.data['name'] = obj.name
#         scheduler.modify_job(obj.name, kwargs=request.data)
#         if request.data.get('spiders'):
#             request.data['spiders'] = str(request.data.get('spiders'))
#         s = serializers.TaskSerializers(obj.jobinfo, request.data)
#         if s.is_valid():
#             s.save()
#             return Response(s.data)
#         return Response(s.errors,status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self,request,pk,format=None):
#         """
#         删除job作业
#         """
#         obj = self.get_object(pk)
#         scheduler.remove_job(obj.name)
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#
# @api_view(['POST'])
# def task_switch(request):
#     """
#     task swicth ,need two params
#     task_name : task name
#     comm : resume or pause
#     """
#     if request.method == 'POST':
#         try:
#             obj = models.DjangoJob.objects.get(name=request.data.get('task_name'))
#         except models.Project.DoesNotExist:
#             raise Http404
#         if request.data.get('comm'):
#             if request.data.get('comm') == 'pause':
#                 scheduler.pause_job(obj.name)
#                 obj.jobinfo.is_active = False
#             if request.data.get('comm') == 'resume':
#                 scheduler.resume_job(obj.name)
#                 obj.jobinfo.is_active = True
#             obj.jobinfo.save()
#             return Response({"status":'success',"message":model_to_dict(obj.jobinfo)})
#         return Response({'status':'error',"message":"params error"},status=status.HTTP_400_BAD_REQUEST)
#
#
# # class EmailScheduler(APIView):
# #
# #     def get(self,request,format=None):
# #         """
# #         get email-scheduler-job info
# #         """
# #         email_job = models.DjangoJob.objects.filter(name='email_scheduler').first()
# #         if email_job:
# #             job = scheduler.get_job(job_id=email_job.name)
# #             info = get_schedulerjob_info(job=job)
# #             return Response(info)
# #         return Response({'status': 'error','message':'email scheduler do not exist'})
# #
# #     def post(self,request,format=None):
# #         """
# #         create a email-scheduler-job
# #         need params:
# #         crontab : 任务调度计划时间，crontab的校验需要前端限制一下
# #         """
# #         email_job = models.DjangoJob.objects.filter(name='email_scheduler').first()
# #         if not email_job:
# #             crontab = request.data.get('crontab')
# #             if not crontab:
# #                 crontab = '00 10 * * *'
# #             job = scheduler.add_job(send_mass_email,CronTrigger.from_crontab(crontab),id='email_scheduler')
# #             info = get_schedulerjob_info(job=job)
# #             return Response(info,status=status.HTTP_201_CREATED)
# #         return Response({'status':"error","message":'email-scheduler-job is exist'},status=status.HTTP_400_BAD_REQUEST)
# #
# #     def put(self,request,format=None):
# #         """
# #         修改邮箱功能调度时间，need params：
# #         crrontab: 调度时间
# #         """
# #         crontab = request.data.get('crontab')
# #         if crontab:
# #             job = scheduler.reschedule_job(job_id='email_scheduler',trigger=CronTrigger.from_crontab(crontab))
# #             info = get_schedulerjob_info(job=job)
# #             return Response(info)
# #         return Response({"status": "error", "message": "Parameter Error"},status=status.HTTP_400_BAD_REQUEST)
# #
# #     def delete(self,request,format=None):
# #         scheduler.remove_job(job_id='email_scheduler')
# #         return Response(status=status.HTTP_204_NO_CONTENT)
#

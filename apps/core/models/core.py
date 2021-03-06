# __author__ = "Amos"
# Email: 379833553@qq.com

from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=255,unique=True)
    ip = models.GenericIPAddressField(max_length=255, blank=True, null=True)
    port = models.IntegerField(default=6800, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    auth = models.BooleanField(default=False)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2,default="0")

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=255,unique=True,default=None)
    description = models.CharField(max_length=255, null=True, blank=True)
    egg = models.CharField(max_length=255, null=True, blank=True)
    built_at = models.DateTimeField(default=None, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Deploy(models.Model):
    client = models.ForeignKey(Client,related_name='cli_deploy', on_delete=models.CASCADE)
    project = models.ForeignKey(Project,related_name='pro_deploy', on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True, null=True)
    deployed_at = models.DateTimeField(default=None, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('client', 'project')


class EmailRecord(models.Model):
    code = models.CharField(max_length=128)
    send_type = models.CharField(max_length=50)
    email = models.EmailField(max_length=128)
    expire_time = models.DateTimeField()
    is_use = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)


# class Task(models.Model):
#     name = models.OneToOneField(DjangoJob,related_name='jobinfo',on_delete=models.CASCADE)
#     client = models.ForeignKey(Client,related_name='cli_tasks',unique=False, on_delete=models.DO_NOTHING)
#     project = models.ForeignKey(Project,related_name='pro_tasks',on_delete=models.DO_NOTHING)
#     spiders = models.TextField(null=True, blank=True)
#     crontab = models.TextField(null=True, blank=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return self.name.name


# class ScrapydJobLog(models.Model):
#     client = models.ForeignKey(Client,related_name='cli_logs',on_delete=models.CASCADE)
#     project = models.ForeignKey(Project,related_name='pro_logs',on_delete=models.DO_NOTHING)
#     spider = models.CharField(max_length=255)
#     job = models.CharField(max_length=255)
#     task = models.ForeignKey(DjangoJob,null=True,blank=True,related_name='joblog',on_delete=models.DO_NOTHING)
#     created_at = models.DateTimeField(auto_now_add=True)


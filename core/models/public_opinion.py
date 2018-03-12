# __author__ = "Amos"
# Email: 379833553@qq.com

from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    info = models.CharField(default='模拟客商信息',max_length=20)

    def __str__(self):
        return self.name


class Keyword(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OaUsersInfo(models.Model):
    full_name = models.CharField(max_length=20)
    oa_user_id = models.CharField(max_length=64)
    email = models.EmailField(null=True,blank=True)
    status = models.BooleanField(default=True)
    is_send_email = models.BooleanField(default=False)

    # 其他信息已实际从OA同步过来的用户数据为准
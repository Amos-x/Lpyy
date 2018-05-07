# __author__ = "Amos"
# Email: 379833553@qq.com

from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=255)
    uscc = models.CharField(max_length=20,unique=True)
    is_active = models.BooleanField(default=True)
    check_url = models.CharField('查询网址',max_length=500,blank=True,null=True)
    type = models.CharField('类型',max_length=255,blank=True,null=True)
    lr = models.CharField('法人',max_length=10,blank=True,null=True)
    registered_capital = models.FloatField('注册资金，单位：万元',blank=True,null=True)
    estab_date = models.DateField('创立时间',blank=True,null=True)
    djjg = models.CharField('登记机关',max_length=255,blank=True,null=True)
    hz_date = models.DateField('核准日期',blank=True,null=True)
    djzt = models.CharField('登记状态',max_length=50,blank=True,null=True)
    address = models.CharField('住所',max_length=255,blank=True,null=True)
    jyfw = models.TextField('经验范围',blank=True,null=True)
    subcompany = models.ManyToManyField('self')

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
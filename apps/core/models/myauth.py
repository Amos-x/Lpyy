# __author__ = "Amos"
# Email: 379833553@qq.com

from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin


class MyUserManager(BaseUserManager):

    def create_user(self,username,email,full_name,password=None):
        """
        创建并保存用户，必填email，用户名，密码
        """
        if not email:
            raise ValueError('User must have an email address')
        if not full_name:
            raise ValueError('The user must fill in the full name')
        if not username:
            raise ValueError('The username is required')

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            full_name = full_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,username,email,full_name,password):
        """
        创建超级管理员用户
        """
        user = self.create_user(
            username = username,
            email = email,
            full_name = full_name,
            password = password
        )

        user.is_admin = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser,PermissionsMixin):
    """
    自定义用户字段信息,拓展User类
    """
    email = models.EmailField(max_length=128,verbose_name='email address')
    username = models.CharField('用户名',max_length=32,unique=True)
    full_name = models.CharField('真实姓名',max_length=10)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    create_date = models.DateField('创建时间',auto_now_add=True,blank=True)

    objects = MyUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['full_name','email']

    def get_full_name(self):
        # 用户的正式标识符，如全名
        return '%s/%s' %(self.username,self.full_name)

    def get_short_name(self):
        # 用户的简短的非正式标识符，例如他们的名字
        return  self.full_name

    def __str__(self):
        return '%s/%s' %(self.username,self.full_name)

    # 下面两个函数，如果不加会没有权限无法进入admin管理界面
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """是否可以进入admin管理界面，默认所有管理员都可以进入"""
        return self.is_admin

    class Meta:
        verbose_name = '用户信息',
        verbose_name_plural = '用户信息'
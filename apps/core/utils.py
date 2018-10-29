# __author__ = "Amos"
# Email: 379833553@qq.com

import configparser,re
from os.path import join
from scrapyd_api import ScrapydAPI
from django.core.mail import send_mail,BadHeaderError
import os
import string
import random
from django.conf import settings
from .models import EmailRecord
import datetime
from django.utils import timezone
import re


def config(path, section, option, name='scrapy.cfg', default=None):
    try:
        cf = configparser.ConfigParser()
        cfg_path = join(path, name)
        cf.read(cfg_path)
        return cf.get(section, option)
    except configparser.NoOptionError:
        return default


def get_scrapyd(client):
    if not client.auth:
        return ScrapydAPI(scrapyd_url(client.ip, client.port))
    return ScrapydAPI(scrapyd_url(client.ip, client.port), auth=(client.username, client.password))


def scrapyd_url(ip, port):
    url = 'http://{ip}:{port}'.format(ip=ip, port=port)
    return url


def scrapyd_status_url(ip,port):
    url = 'http://{ip}:{port}/daemonstatus.json'.format(ip=ip, port=port)
    return url


def get_schedulerjob_info(job):
    a = re.findall(r"'(.+?)'", str(job.trigger))
    b = a.pop(2)
    a.reverse()
    a.append(b)
    crontab = ' '.join(a)
    info = {
        'status': 'ok',
        'name': job.id,
        'crontab': crontab,
        'next_run_time': job.next_run_time,
    }
    return info


def get_project_path(project_name=None):
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                        settings.PROJECTS_FOLDER)
    if project_name:
        return os.path.join(path, project_name)
    else:
        return path


# 随机产生字符串验证码
def random_captcha(codelength=50):
    chars = string.ascii_lowercase+string.ascii_uppercase+string.digits
    return ''.join(random.choice(chars) for i in range(codelength))


def send_mail_to_user(email,send_type='register', user_id=''):
    code = random_captcha()
    if send_type == 'register':
        mail_title = 'Lpyy 账户激活'
        mail_body = """
点击以下链接，激活您的账号：
http://{0}:{1}/userinfo/reset_passwd/{2}

                
为保障您的帐号安全，请在24小时内点击该链接，您也可以将链接复制到浏览器地址栏访问。如果您并未尝试激活邮箱，请忽略本邮件，由此给您带来的不便请谅解。

本邮件由系统自动发出，请勿直接回复！
        """.format(settings.LOCAL_DOMAIN,settings.HTTP_LISTEN_PORT,code)
    elif send_type == 'forgot':
        mail_title = 'Lpyy 重置密码'
        mail_body = """
点击以下链接，重置您的密码：
http://{0}:{1}/userinfo/reset_passwd/{2}

                
为保障您的帐号安全，请在24小时内点击该链接，您也可以将链接复制到浏览器地址栏访问。如果您并未尝试激活邮箱，请忽略本邮件，由此给您带来的不便请谅解。

本邮件由系统自动发出，请勿直接回复！
        """.format(settings.LOCAL_DOMAIN,settings.HTTP_LISTEN_PORT,code)
    elif send_type == 'change_email':
        mail_title = 'Lpyy 修改邮箱，激活绑定邮箱'
        mail_body = """
点击以下链接，绑定新邮箱：
http://{0}:{1}/userinfo/reset_email/{2}/{3}

                
为保障您的帐号安全，请在24小时内点击该链接，您也可以将链接复制到浏览器地址栏访问。如果您并未尝试激活邮箱，请忽略本邮件，由此给您带来的不便请谅解。

本邮件由系统自动发出，请勿直接回复！
        """.format(settings.LOCAL_DOMAIN,settings.HTTP_LISTEN_PORT,user_id,code)
    else:
        return 0

    try:
        status = send_mail(mail_title,mail_body,settings.DEFAULT_FROM_EMAIL,[email])
    except Exception as e:
        return 0

    if status == 1:
        email_record = EmailRecord()
        email_record.code = code
        email_record.send_type = send_type
        email_record.email = email
        email_record.expire_time = timezone.now() + datetime.timedelta(1)
        email_record.save()

    return status


def is_email(str):
    if re.match("^[a-zA-Z0-9_\-]+@[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+$", str):
        return True
    else:
        return False


# __author__ = "Amos"
# Email: 379833553@qq.com

from __future__ import absolute_import, unicode_literals
from celery import shared_task
from . import models
from .utils import get_scrapyd,scrapyd_status_url
from django.conf import settings
from django.core.mail import send_mail
import requests,json
import logging

logger = logging.getLogger('scheduler_task')


@shared_task
def check_clients_status():
    """
    get scrapy clients status

    """
    clients = models.Client.objects.all()
    error_obj = []
    success_obj = []
    for client_obj in clients:
        try:
            url = scrapyd_status_url(client_obj.ip,client_obj.port)
            response = requests.get(url,timeout=2)
            if response.status_code == 200:
                client_obj.objects.update(status='1')
                success_obj.append(client_obj.name)
        except:
            error_obj.append(client_obj.name)
    return {'succes':success_obj,'error':error_obj}


@shared_task
def spider_scheduler(client,project,spiders=None):
    """
    Use celery scheduler spiders

    You need scrapyd's client id ,project id and spiders,if spiders is None
    default crawl all spiders in project.

    Example:
        spider_scheduler.delay(1,2,['spider1','spider2'])

    """
    client_obj = models.Client.objects.filter(id=client).first()
    if client_obj:
        scrapyd = get_scrapyd(client_obj)
        pro_obj = models.Project.objects.filter(id=project).first()
        if pro_obj:
            if spiders:
                spider_list = spiders
            else:
                spider_list = scrapyd.list_spiders(project)
            result = []
            for spider in spider_list:
                job = scrapyd.schedule(project, spider)
                logger.info("Crawl {} {} Finished".format(pro_obj.name,spider))
                result.append({"client":client,"project":project,"spider":spider,"job":job})
            return result
        else:
            raise ValueError('Project dont exist')
    else:
        raise ValueError('Client dont exist')


@shared_task
def send_mail_async(*args, **kwargs):
    """ Using celery to send email async

    You can use it as django send_mail function

    Example:
    send_mail_sync.delay(subject, message, from_mail, recipient_list, fail_silently=False, html_message=None)

    Also you can ignore the from_mail, unlike django send_mail, from_email is not a require args:

    Example:
    send_mail_sync.delay(subject, message, recipient_list, fail_silently=False, html_message=None)
    """
    if len(args) == 3:
        args = list(args)
        args[0] = settings.EMAIL_SUBJECT_PREFIX + args[0]
        args.insert(2, settings.EMAIL_HOST_USER)
        args = tuple(args)

    try:
        send_mail(*args, **kwargs)
    except Exception as e:
        logger.error("Sending mail error: {}".format(e))

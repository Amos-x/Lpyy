# __author__ = "Amos"
# Email: 379833553@qq.com

import configparser,re
from os.path import join
from scrapyd_api import ScrapydAPI
from django.core.mail import send_mail,BadHeaderError


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


def send_email(request):
    subject = request.POST.get('subject')
    message = request.POST.get('message')
    from_email = request.POST.get('from_email')
    to_email = request.POST.get('to_email')
    if subject and message and from_email:
        try:
            send_mail(subject, message, from_email, to_email)
        except BadHeaderError:
            return {'status':'error','message':'Invalid header found'}
        return {'status':'ok','message':'Success send email'}
    else:
        return {'status':'error','message':'Make sure all fields are entered and valid'}


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
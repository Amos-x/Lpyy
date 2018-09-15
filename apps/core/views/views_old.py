from django.shortcuts import render,HttpResponse
from .. import models
import requests


def joblog(request,c,p,s,j):
    """ get job's log """
    if request.method == 'GET':
        if c and p and s and j:
            try:
                client_obj = models.Client.objects.get(id=c)
                url = 'http://{ip}:{port}/logs/{project}/{spider}/{job}.log'.format(ip=client_obj.ip,
                                                                                   port=client_obj.port,
                                                                                    project=p,
                                                                                    spider=s,
                                                                                    job=j)
                response = requests.get(url, timeout=5,
                                        auth=(client_obj.username, client_obj.password) if client_obj.auth else None)
                if response.status_code == 200:
                    return HttpResponse(response.text,content_type='text/plain')
            except:
                pass
        return HttpResponse(status=400)

# __author__ = "Amos"
# Email: 379833553@qq.com

from __future__ import absolute_import, unicode_literals
from celery import shared_task


@shared_task
def testtask(x,y):
    return x+y

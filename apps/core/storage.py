# -*- coding:utf-8 -*-
# __author__: Amos
# Email：379833553@qq.com
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import time
import random


class ImageStorage(FileSystemStorage):
    def __init__(self,location=settings.MEDIA_ROOT,base_url=settings.MEDIA_URL):
        super(ImageStorage,self).__init__(location,base_url)

    def _save(self, name, content):
        ext = os.path.splitext(name)[1]
        dir = os.path.dirname(name)
        filename = time.strftime('%Y%m%d%H%M%S')
        filename = filename + '_%d' %random.randint(0,100)
        name = os.path.join(dir,filename + ext)
        return super(ImageStorage, self)._save(name=name,content=content)
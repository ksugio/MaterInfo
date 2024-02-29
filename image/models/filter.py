from django.db import models
from django.utils.module_loading import import_string
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from project.models import Created, Updated, Remote, ModelUploadTo
from .image import Image
from io import BytesIO
import os
import cv2
import numpy as np
import PIL

def cv2PIL(cvimg):
    newimg = cvimg.copy()
    if newimg.ndim == 2:
        pass
    elif newimg.shape[2] == 3:
        newimg = cv2.cvtColor(newimg, cv2.COLOR_BGR2RGB)
    elif newimg.shape[2] == 4:
        newimg = cv2.cvtColor(newimg, cv2.COLOR_BGRA2RGBA)
    return PIL.Image.fromarray(newimg)

def PIL2cv(pilimg):
    newimg = np.array(pilimg, dtype=np.uint8)
    if newimg.ndim == 2:
        pass
    elif newimg.shape[2] == 3:
        newimg = cv2.cvtColor(newimg, cv2.COLOR_RGB2BGR)
    elif newimg.shape[2] == 4:
        newimg = cv2.cvtColor(newimg, cv2.COLOR_RGBA2BGRA)
    return newimg

class Filter(Created, Updated, Remote):
    upper = models.ForeignKey(Image, verbose_name='Image', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    template = models.BooleanField(verbose_name='Template', default=False)
    FormatChoices = ((0, 'PNG'), (1, 'JPEG'))
    format = models.PositiveSmallIntegerField(verbose_name='Format', choices=FormatChoices, default=0)
    alias = models.IntegerField(verbose_name='Alias ID', blank=True, null=True)
    file = models.ImageField(verbose_name='Image', upload_to=ModelUploadTo, blank=True, null=True)
    pixelsize = models.FloatField(verbose_name='Pixel Size', blank=True, null=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('image:filter_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('image:filter_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('image:filter_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('image:filter_delete', kwargs={'pk': self.id})

    def pathname(self):
        return '%s/%s' % (self.upper.upper, self.upper)

    def entity_id(self):
        if self.alias:
            return self.alias
        else:
            return self.id

    def process_updated_at(self):
        cls = import_string('image.models.process.Process')
        updated_at = self.upper.updated_at
        if self.alias:
            source = Filter.objects.get(pk=self.alias)
            processes = cls.objects.filter(upper=source)
            for process in processes:
                if process.updated_at > updated_at:
                    updated_at = process.updated_at
        else:
            processes = cls.objects.filter(upper=self)
            for process in processes:
                if process.updated_at > updated_at:
                    updated_at = process.updated_at
        return updated_at

    def recent_updated_at(self):
        updated_at = self.process_updated_at()
        if self.updated_at > updated_at:
            updated_at = self.updated_at
        return updated_at

    def save_img(self, img):
        pilimg = cv2PIL(img)
        buf = BytesIO()
        if self.format == 0:
            pilimg.save(buf, format='png')
            filename = '%s%s.png' % (self.upper.__class__.__name__, self.__class__.__name__)
        elif self.format == 1:
            pilimg.save(buf, format='jpeg')
            filename = '%s%s.jpg' % (self.upper.__class__.__name__, self.__class__.__name__)
        self.file.save(filename, buf, save=False)
        buf.close()

    def read_img(self):
        with self.file.open('rb') as f:
            binary = f.read()
            arr = np.asarray(bytearray(binary), dtype=np.uint8)
            return cv2.imdecode(arr, -1)
        return None

    def check_read_img(self):
        if self.updated_at < self.process_updated_at():
            self.savefile()
            self.save()
        return self.read_img()

    def procimg(self, img, procid=0, sizeprocess=False):
        img = img.copy()
        cls = import_string('image.models.process.Process')
        if self.alias:
            source = Filter.objects.get(pk=self.alias)
            processes = cls.objects.filter(upper=source).order_by('order')
        else:
            processes = cls.objects.filter(upper=self).order_by('order')
        kwargs = {'pixelsize': self.upper.pixelsize()}
        if sizeprocess:
            for process in processes:
                if hasattr(process.entity(), 'sizeprocess'):
                    img, kwargs = process.process(img, **kwargs)
                if process.id == procid:
                    break
        else:
            for process in processes:
                img, kwargs = process.process(img, **kwargs)
                if process.id == procid:
                    break
        return img, kwargs

    def savefile(self):
        img = self.upper.read_img()
        img, kwargs = self.procimg(img)
        self.save_img(img)
        self.pixelsize = kwargs['pixelsize']

    def sizeprocess(self, img, **kwargs):
        for proc in kwargs['sizeprocess']:
            if proc['type'] == 'resize':
                img = cv2.resize(img, (proc['width'], proc['height']))
            elif proc['type'] == 'trim':
                img = img[proc['starty']:proc['endy'], proc['startx']:proc['endx']]
        return img

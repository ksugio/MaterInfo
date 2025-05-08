from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, ModelUploadTo, Unique
from sample.models import Sample
import cv2
import numpy as np

def ImageUploadTo(instance, filename):
    return filename

class Image(Created, Updated, Remote, Unique):
    upper = models.ForeignKey(Sample, verbose_name='Sample', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    file = models.ImageField(verbose_name='Image', upload_to=ModelUploadTo)
    scale = models.FloatField(verbose_name='Scale', default=1.0)
    UnitChoices = ((0, 'pixel'), (1, 'kilometer'), (2, 'meter'), (3, 'millimeter'), (4, 'micrometer'), (5, 'nanometer'))
    UnitText = ('px', 'km', 'm', 'mm', '\u03bcm', 'nm')
    scaleunit = models.PositiveSmallIntegerField(verbose_name='Scale unit', choices=UnitChoices, default=0)
    scalepixels = models.PositiveIntegerField(verbose_name='Scale pixels', default=1)
    DeviceChoices = ((0, 'Camera'), (1, 'OM'), (2, 'SEM'), (3, 'EPMA'), (4, 'EDS'), (5, 'EBSD'), (6, 'TEM'), (7, 'XRAY'))
    device = models.PositiveSmallIntegerField(verbose_name='Device', choices=DeviceChoices, default=0)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('image:list', kwargs={'pk': self.upper.id, 'order': 0, 'size': 0})

    def get_detail_url(self):
        return reverse('image:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('image:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('image:delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('image:api_update', kwargs={'pk': self.id})

    def pixelsize(self):
        return self.scale / self.scalepixels

    def unittext(self):
        return self.UnitText[self.scaleunit]

    def read_img(self):
        with self.file.open('rb') as f:
            binary = f.read()
            arr = np.asarray(bytearray(binary), dtype=np.uint8)
            return cv2.imdecode(arr, -1)
        return None

from django.utils.module_loading import import_string
from django.db import models
from django.urls import reverse
from project.models import Updated, Remote, FileSearch
from .album import Album
from PIL import Image
from io import BytesIO
import requests

class Item(Updated, Remote, FileSearch):
    upper = models.ForeignKey(Album, verbose_name='Album', on_delete=models.CASCADE)
    url = models.CharField(verbose_name='URL', max_length=256)
    width = models.PositiveSmallIntegerField(verbose_name='Width', blank=True, null=True)
    height = models.PositiveSmallIntegerField(verbose_name='Height', blank=True, null=True)
    shiftx = models.SmallIntegerField(verbose_name='Shift X', default=0)
    shifty = models.SmallIntegerField(verbose_name='Shift Y', default=0)
    order = models.SmallIntegerField(verbose_name='Order')

    def title(self):
        return '%s : %s_%d' % (self.upper.title, self.name(), self.order)

    def name(self):
        return self.__class__.__name__

    def get_detail_url(self):
        return reverse('album:update', kwargs={'pk': self.upper.id})

    def get_update_url(self):
        return reverse('album:item_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('album:item_delete', kwargs={'pk': self.id})

    def get_image_url(self):
        return reverse('album:item_image', kwargs={'pk': self.id})

    def get_image(self, **kwargs):
        if self.url.startswith('http'):
            response = requests.get(self.url)
            if response.status_code != 200 or 'image' not in response.headers['Content-Type']:
                return Image.new('L', (640, 480), 128)
            else:
                src = Image.open(BytesIO(response.content))
        else:
            file = self.file_search(self.url)
            if file is None:
                return Image.new('L', (640, 480), 128)
            else:
                src = Image.open(file)
        if self.width is not None and self.height is not None:
            return src.resize((self.width, self.height))
        elif self.width is not None:
            w, h = src.size
            height = int(h / w * self.width)
            return src.resize((self.width, height))
        elif self.height is not None:
            w, h = src.size
            width = int(w / h * self.height)
            return src.resize((width, self.height))
        else:
            return src

    def detail_url(self):
        return self.detail_search(self.url)

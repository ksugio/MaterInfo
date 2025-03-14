from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote
from .article import Article
from io import BytesIO
import pymupdf

class Image(Created, Updated, Remote):
    upper = models.ForeignKey(Article, verbose_name='Article', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    note = models.TextField(verbose_name='Note', blank=True)
    page = models.PositiveSmallIntegerField(verbose_name='Page', default=1)
    scale = models.FloatField(verbose_name='Scale', default=1.0)
    rotate = models.FloatField(verbose_name='Rotate angle', default=0)
    startx = models.PositiveSmallIntegerField(verbose_name='Start x', default=0)
    starty = models.PositiveSmallIntegerField(verbose_name='Start y', default=0)
    endx = models.PositiveSmallIntegerField(verbose_name='End x', default=0)
    endy = models.PositiveSmallIntegerField(verbose_name='End y', default=0)
    zoom = models.PositiveSmallIntegerField(verbose_name='Zoom', default=100)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('reference:image_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('reference:image_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('reference:image_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('reference:image_delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('reference:api_image_update', kwargs={'pk': self.id})

    def get_pixmap(self, page, scale, rotate):
        with self.upper.file.open('rb') as f:
            buf = BytesIO(f.read())
            doc = pymupdf.open(stream=buf.getvalue(), filetype='pdf')
            if page - 1 <= doc.page_count:
                matrix = pymupdf.Matrix(pymupdf.Identity)
                if scale != 1.0:
                    matrix.prescale(scale, scale)
                if rotate != 0:
                    matrix.prerotate(rotate)
                pixmap = doc[page - 1].get_pixmap(matrix=matrix)
            else:
                pixmap = None
            buf.close()
        return pixmap

    def get_trim_pixmap(self):
        pixmap = self.get_pixmap(self.page, self.scale, self.rotate)
        if pixmap is not None:
            width = self.endx - self.startx
            height = self.endy - self.starty
            if width == 0:
                width = pixmap.width
            if height == 0:
                height = pixmap.height
            pixmap.set_origin(-self.startx, -self.starty)
            pixmap2 = pymupdf.Pixmap(pixmap.colorspace, (0, 0, width, height))
            pixmap2.copy(pixmap, (0, 0, width, height))
        else:
            pixmap2 = None
        return pixmap2
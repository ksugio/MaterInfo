from django.db import models
from django.utils.module_loading import import_string
from project.models import Project, Created, Updated, Remote, ModelUploadTo, Unique
from django.urls import reverse
from image.models.process import ColorTable, ColorChoices
from io import BytesIO
import PIL
import math as m

class Album(Created, Updated, Remote, Unique):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    ncol = models.PositiveSmallIntegerField(verbose_name='N Column', default=1)
    margin = models.PositiveSmallIntegerField(verbose_name='Margin', default=0)
    bgcolor = models.PositiveSmallIntegerField(verbose_name='BG Color', choices=ColorChoices, default=0)
    FormatChoices = ((0, 'JPEG'), (1, 'PNG'))
    format = models.PositiveSmallIntegerField(verbose_name='Format', choices=FormatChoices, default=0)
    file = models.ImageField(verbose_name='Image', upload_to=ModelUploadTo, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('album:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('album:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('album:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('album:delete', kwargs={'pk': self.id})

    def get_image_url(self):
        return reverse('album:image', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('album:api_update', kwargs={'pk': self.id})

    def bgcolor_rgb(self):
        return ColorTable[self.bgcolor]

    def tile(self, images, shifts):
        if len(images) == 0:
            return PIL.Image.new(mode='RGB', size=(1, 1), color=self.bgcolor_rgb())
        x = 0
        y = 0
        nrow = int(m.ceil(len(images) / self.ncol))
        maxw = 0
        pos = []
        for j in range(nrow):
            x = 0
            maxh = 0
            for i in range(self.ncol):
                p = j * self.ncol + i
                if p >= len(images):
                    break
                x = x + shifts[p][0]
                pos.append((x, y + shifts[p][1]))
                size = images[p].size
                x = x + self.margin + size[0]
                h = shifts[p][1] + size[1]
                if h > maxh:
                    maxh = h
            w = x - self.margin
            if w > maxw:
                maxw = w
            y = y + self.margin + maxh
        pilimg = PIL.Image.new(mode='RGB', size=(maxw, y - self.margin), color=self.bgcolor_rgb())
        for i in range(len(images)):
            pilimg.paste(images[i], pos[i])
        return pilimg

    def saveimg(self, request):
        cls = import_string('album.models.item.Item')
        items = cls.objects.filter(upper=self).order_by('order')
        images = []
        shifts = []
        for item in items:
            images.append(item.get_image(request_host=request._current_scheme_host,
                                         request_cookies=request.COOKIES))
            shifts.append([item.shiftx, item.shifty])
        pilimg = self.tile(images, shifts)
        buf = BytesIO()
        if self.format == 0:
            pilimg.save(buf, format='jpeg')
            filename = '%s.jpg' % self.__class__.__name__
        elif self.format == 1:
            pilimg.save(buf, format='png')
            filename = '%s.png' % self.__class__.__name__
        self.file.save(filename, buf, save=False)
        buf.close()

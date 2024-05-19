from config.settings import IMAGE_FILTER_PROCESS, FONT_PATH
from django.urls import reverse
from django.utils.module_loading import import_string
from django.db import models
from django.core.exceptions import ValidationError
from project.models import Updated, Remote
from .filter import Filter, cv2PIL, PIL2cv
from PIL import ImageDraw, ImageFont
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ColorTable = ((255, 255, 255), (128, 128, 0), (255, 255, 0), (255, 0, 255),
              (192, 192, 192), (0, 255, 255), (0, 255, 0), (255, 0, 0),
              (128, 128, 128), (0, 0, 255), (0, 128, 0), (128, 0, 128),
              (0, 0, 0), (0, 0, 128), (0, 128, 128), (128, 0, 0))

ColorChoices = ((0, 'White'), (1, 'Olive'), (2, 'Yellow'), (3, 'Fuchsia'),
                (4, 'Silver'), (5, 'Aqua'), (6, 'Lime'), (7, 'Red'),
                (8, 'Gray'), (9, 'Blue'), (10, 'Green'), (11, 'Purple'),
                (12, 'Black'), (13, 'Navy'), (14, 'Teal'), (15, 'Maroon'))

class Process(Updated, Remote):
    upper = models.ForeignKey(Filter, verbose_name='Filter', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Name', max_length=16, blank=True)
    order = models.SmallIntegerField(verbose_name='Order')

    def title(self):
        return '%s : %s_%d' % (self.upper.title, self.name, self.order)

    def get_detail_url(self):
        return reverse('image:filter_update', kwargs={'pk': self.upper.id})

    def get_update_url(self):
        pass

    def get_delete_url(self):
        return reverse('image:process_delete', kwargs={'pk': self.id})

    def get_image_url(self):
        return reverse('image:filter_image', kwargs={'pk': self.upper.id, 'procid': self.id})

    def get_histgram_url(self):
        return reverse('image:filter_histgram', kwargs={'pk': self.upper.id, 'procid': self.id})

    def entity(self):
        if self.name:
            for item in IMAGE_FILTER_PROCESS:
                if item['Model'].split('.')[-1] == self.name:
                    cls = import_string(item['Model'])
                    return cls.objects.get(id=self.id)
        else:
            for item in IMAGE_FILTER_PROCESS:
                cls = import_string(item['Model'])
                obj = cls.objects.filter(id=self.id)
                if obj:
                    return obj[0]

    def process(self, img, **kwargs):
        return self.entity().process(img, **kwargs)

class Resize(Process):
    width = models.PositiveSmallIntegerField(verbose_name='Width', default=0)
    height = models.PositiveSmallIntegerField(verbose_name='Height', default=0)

    def process(self, src, **kwargs):
        if self.width > 0  and self.height > 0:
            dst = cv2.resize(src, (self.width, self.height))
            kwargs['pixelsize'] *= src.shape[1] / self.width
        elif self.width > 0:
            height = int(src.shape[0] / src.shape[1] * self.width)
            dst = cv2.resize(src, (self.width, height))
            kwargs['pixelsize'] *= src.shape[1] / self.width
        elif self.height > 0:
            width = int(src.shape[1] / src.shape[0] * self.height)
            dst = cv2.resize(src, (width, self.height))
            kwargs['pixelsize'] *= src.shape[1] / width
        else:
            dst = src
        return dst, kwargs

    def sizeprocess(self, src, **kwargs):
        return self.process(src, **kwargs)

    def get_update_url(self):
        return reverse('image:resize_update', kwargs={'pk': self.id})

class Trim(Process):
    startx = models.PositiveSmallIntegerField(verbose_name='StartX', default=0)
    starty = models.PositiveSmallIntegerField(verbose_name='StartY', default=0)
    endx = models.PositiveSmallIntegerField(verbose_name='EndX', default=0)
    endy = models.PositiveSmallIntegerField(verbose_name='EndY', default=0)

    def process(self, src, **kwargs):
        width = self.endx - self.startx
        height = self.endy - self.starty
        if width > 0 and height > 0:
            return src[self.starty:self.endy, self.startx:self.endx].copy(), kwargs
        else:
            return src, kwargs

    def sizeprocess(self, src, **kwargs):
        return self.process(src, **kwargs)

    def get_update_url(self):
        return reverse('image:trim_update', kwargs={'pk': self.id})\

def CheckOdd(value):
    if value % 2 == 0:
        raise ValidationError('Input odd number')

class Smoothing(Process):
    MethodChoices = ((0, 'Blur'), (1, 'Gaussian'), (2, 'Median'), (3, 'Bilateral'))
    method = models.PositiveSmallIntegerField(verbose_name='Method', choices=MethodChoices, default=0)
    size = models.PositiveSmallIntegerField(verbose_name='Size', default=3, validators=[CheckOdd])
    sigma0 = models.FloatField(verbose_name='Sigma0', default=1.0)
    sigma1 = models.FloatField(verbose_name='Sigma1', default=1.0)

    def process(self, src, **kwargs):
        if self.method == 0:
            return cv2.blur(src, (self.size, self.size)), kwargs
        elif self.method == 1:
            return cv2.GaussianBlur(src, (self.size, self.size), self.sigma0, self.sigma1), kwargs
        elif self.method == 2:
            return cv2.medianBlur(src, self.size), kwargs
        elif self.method == 3:
            return cv2.bilateralFilter(src, self.size, self.sigma0, self.sigma1), kwargs
        else:
            return src.copy(), kwargs

    def get_update_url(self):
        return reverse('image:smoothing_update', kwargs={'pk': self.id})

class Threshold(Process):
    MethodChoices = ((0, 'Simple'), (1, 'Otsu'), (2, 'Adaptive Mean'), (3, 'Adaptive Gauss'))
    method = models.PositiveSmallIntegerField(verbose_name='Method', choices=MethodChoices, default=0)
    thresh = models.PositiveSmallIntegerField(verbose_name='Threshold', default=128)
    blocksize = models.PositiveSmallIntegerField(verbose_name='Blocksize', default=3, validators=[CheckOdd])
    parameter = models.SmallIntegerField(verbose_name='Parameter', default=0)
    invert = models.BooleanField(verbose_name='Invert', default=False)

    def process(self, src, **kwargs):
        if len(src.shape) == 3:
            src = cv2.cvtColor(src, cv2.COLOR_RGB2GRAY)
        if self.invert:
            sty = cv2.THRESH_BINARY_INV
        else:
            sty = cv2.THRESH_BINARY
        if self.method == 0:
            ret, dst = cv2.threshold(src, self.thresh, 255, sty)
        elif self.method == 1:
            ret, dst = cv2.threshold(src, 0, 255, sty + cv2.THRESH_OTSU)
        elif self.method == 2:
            dst = cv2.adaptiveThreshold(src, 255, cv2.ADAPTIVE_THRESH_MEAN_C, sty,\
                                        self.blocksize, self.parameter)
        elif self.method == 3:
            dst = cv2.adaptiveThreshold(src, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, sty,\
                                        self.blocksize, self.parameter)
        return dst, kwargs

    def get_update_url(self):
        return reverse('image:threshold_update', kwargs={'pk': self.id})

class Molphology(Process):
    MethodChoices = ((0, 'Opening'), (1, 'Closing'), (2, 'Erosion'), (3, 'Dilation'), (4, 'Gradient'), (5, 'TopHat'), (6, 'BlackHat'))
    method = models.PositiveSmallIntegerField(verbose_name='Method', choices=MethodChoices, default=0)
    iteration = models.PositiveSmallIntegerField(verbose_name='Iteration', default=1)
    kernelsize = models.PositiveSmallIntegerField(verbose_name='KernelSize', default=3)

    def process(self, src, **kwargs):
        kernel = np.ones((self.kernelsize, self.kernelsize), np.uint8)
        if self.iteration > 0:
            if self.method == 0:
                return cv2.morphologyEx(src, cv2.MORPH_OPEN, kernel, iterations=self.iteration), kwargs
            elif self.method == 1:
                return cv2.morphologyEx(src, cv2.MORPH_CLOSE, kernel, iterations=self.iteration), kwargs
            elif self.method == 2:
                return cv2.erode(src, kernel, iterations=self.iteration), kwargs
            elif self.method == 3:
                return cv2.dilate(src, kernel, iterations=self.iteration), kwargs
            elif self.method == 4:
                return cv2.morphologyEx(src, cv2.MORPH_GRADIENT, kernel, iterations=self.iteration), kwargs
            elif self.method == 5:
                return cv2.morphologyEx(src, cv2.MORPH_TOPHAT, kernel, iterations=self.iteration), kwargs
            elif self.method == 6:
                return cv2.morphologyEx(src, cv2.MORPH_BLACKHAT, kernel, iterations=self.iteration), kwargs
        else:
            return src, kwargs

    def get_update_url(self):
        return reverse('image:molphology_update', kwargs={'pk': self.id})

class DrawScale(Process):
    scale = models.CharField(verbose_name='Scale', max_length=32, default=1.0)
    width = models.PositiveSmallIntegerField(verbose_name='Width', default=10)
    fontsize = models.PositiveSmallIntegerField(verbose_name='Fontsize', default=50)
    StatusChoices = ((0, 'BottomRight'), (1, 'TopRight'), (2, 'TopLeft'), (3, 'BottomLeft'))
    pos = models.PositiveSmallIntegerField(verbose_name='Position', choices=StatusChoices, default=0)
    color = models.PositiveSmallIntegerField(verbose_name='Color', choices=ColorChoices, default=0)
    marginx = models.PositiveSmallIntegerField(verbose_name='Margin X', default=10)
    marginy = models.PositiveSmallIntegerField(verbose_name='Margin Y', default=10)
    bg = models.BooleanField(verbose_name='BG', default=False)
    bgcolor = models.PositiveSmallIntegerField(verbose_name='BG Color', choices=ColorChoices, default=0)

    def process(self, src, **kwargs):
        iplimg = cv2PIL(src).convert("RGB")
        scale = float(self.scale)
        w, h = iplimg.size
        sps = scale / kwargs['pixelsize']
        font = ImageFont.truetype(FONT_PATH, self.fontsize)
        color = ColorTable[self.color]
        draw = ImageDraw.Draw(iplimg)
        text = '%s %s' % (self.scale, self.upper.upper.unittext())
        _, _, tw, th = draw.textbbox((0, 0), text=text, font=font)
        mx = self.marginx
        my = self.marginy
        if self.pos == 0:
            lpos = ((w - sps - mx, h - my), (w - mx, h - my))
            tpos = (w - sps / 2 - mx - tw / 2, h - my - th - self.width)
            bpos = ((w - sps - 2 * mx, h - th - 3 * my), (w, h))
        elif self.pos == 1:
            lpos = ((w - sps - mx, my + th + self.width), (w - mx, my + th + self.width))
            tpos = (w - sps / 2 - mx - tw / 2, my)
            bpos = ((w - sps - 2 * mx, 0), (w, th + 3 * my))
        elif self.pos == 2:
            lpos = ((mx, my + th + self.width), (mx + sps, my + th + self.width))
            tpos = (mx + sps / 2 - tw / 2, my)
            bpos = ((0, 0), (sps + 2 * mx, th + 3 * my))
        elif self.pos == 3:
            lpos = ((mx, h - my), (mx + sps, h - my))
            tpos = (mx + sps / 2 - tw / 2, h - my - th - self.width)
            bpos = ((0, h - th - 3 * my), (sps + 2 * mx, h))
        if self.bg:
            bgcolor = ColorTable[self.bgcolor]
            draw.rectangle(bpos, fill=bgcolor, outline=bgcolor)
        draw.line(lpos, fill=color, width=self.width)
        draw.text(tpos, text, fill=color, font=font)
        return PIL2cv(iplimg), kwargs

    def get_update_url(self):
        return reverse('image:drawscale_update', kwargs={'pk': self.id})

def Check256(value):
    if value >= 256:
        raise ValidationError('Input value smaller than 256')

class Tone(Process):
    MethodChoices = ((0, 'Linear'), (1, 'Gamma'), (2, 'Sigmoid'),  (3, 'Solarization'), (4, 'Posterization'))
    method = models.PositiveSmallIntegerField(verbose_name='Method', choices=MethodChoices, default=0)
    min = models.PositiveSmallIntegerField(verbose_name='Min', default=0, validators=[Check256])
    max = models.PositiveSmallIntegerField(verbose_name='Max', default=255, validators=[Check256])
    low = models.PositiveSmallIntegerField(verbose_name='Low', default=0, validators=[Check256])
    high = models.PositiveSmallIntegerField(verbose_name='High', default=255, validators=[Check256])
    invert = models.BooleanField(verbose_name='Invert', default=False)
    option = models.FloatField(verbose_name='Option', blank=True, default=1.0)

    def process(self, src, **kwargs):
        return cv2.LUT(src, self.lut()), kwargs

    def lut(self):
        num = self.max - self.min
        x = np.arange(1, num, 1) / num
        if self.method == 0:
            y = x
        elif self.method == 1:
            y = x ** (1.0 / self.option)
        elif self.method == 2:
            y = 1.0 / (1.0 + np.exp(self.option * (0.5 - x)))
        elif self.method == 3:
            y = 0.5 * np.sin(np.pi * (self.option * x - 0.5)) + 0.5
        elif self.method == 4:
            y = self.posterization(x)
        y = np.round((self.high - self.low) * y + self.low)
        if self.invert:
            start = np.full(self.min + 1, self.high, dtype='uint8')
            end = np.full(256 - self.max, self.low, dtype='uint8')
            y = y[::-1]
        else:
            start = np.full(self.min + 1, self.low, dtype='uint8')
            end = np.full(256 - self.max, self.high, dtype='uint8')
        lut = np.hstack([start, y.astype('uint8'), end])
        return lut

    def posterization(self, x):
        step = int(self.option)
        if step > 1 and step < 256:
            split = 1.0 / (step - 1)
            up = 1.0 / step
            y = []
            for xx in x:
                v = int(xx / up) * split
                if v >= 1.0:
                    y.append(1.0)
                else:
                    y.append(v)
            return np.array(y)
        else:
            return x

    def get_update_url(self):
        return reverse('image:tone_update', kwargs={'pk': self.id})

    def get_plot_url(self):
        return reverse('image:tone_plot', kwargs={'pk': self.id})

    def plot(self, **kwargs):
        plt.figure(figsize=(5, 5))
        plt.plot(range(256), self.lut())
        plt.xlim(-10, 265)
        plt.ylim(-10, 265)
        plt.xlabel('Input')
        plt.ylabel('Output')

class Transform(Process):
    MethodChoices = ((0, 'Rotate'), (1, 'Rotate90'), (2, 'Rotate-90'), (3, 'Rotate180'),
                     (4, 'UpDown'), (5, 'LeftRight'), (6, 'UpDownLeftRight'))
    method = models.PositiveSmallIntegerField(verbose_name='Method', choices=MethodChoices, default=0)
    angle = models.FloatField(verbose_name='Angle', default=0)

    def process(self, src, **kwargs):
        if self.method == 0:
            return self.rotate(src), kwargs
        elif self.method == 1:
            return cv2.rotate(src, cv2.ROTATE_90_CLOCKWISE), kwargs
        elif self.method == 2:
            return cv2.rotate(src, cv2.ROTATE_90_COUNTERCLOCKWISE), kwargs
        elif self.method == 3:
            return cv2.rotate(src, cv2.ROTATE_180), kwargs
        elif self.method == 4:
            return cv2.flip(src, 0), kwargs
        elif self.method == 5:
            return cv2.flip(src, 1), kwargs
        elif self.method == 6:
            return cv2.flip(src, -1), kwargs
        else:
            return src, kwargs

    def rotate(self, src):
        h, w = src.shape[:2]
        a = np.radians(-self.angle)
        wrot = w*abs(np.cos(a))+h*abs(np.sin(a))
        hrot = w*abs(np.sin(a))+h*abs(np.cos(a))
        mat = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), -self.angle, 1.0)
        mat[0][2] += -w / 2.0 + wrot / 2.0
        mat[1][2] += -h / 2.0 + hrot / 2.0
        return cv2.warpAffine(src, mat, (int(wrot), int(hrot)))

    def get_update_url(self):
        return reverse('image:transform_update', kwargs={'pk': self.id})

#class Watershed(Process):
#    fgurl = models.CharField(verbose_name='Foreground URL', max_length=256)
#
#    def process(self, src, **kwargs):
#        return src, kwargs
#
#    def get_update_url(self):
#        return reverse('image:watershed_update', kwargs={'pk': self.id})

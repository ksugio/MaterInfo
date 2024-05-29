from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, PrefixPtr, ModelUploadTo, Unique
from .filter import Filter, cv2PIL
from io import BytesIO
import MPLn23d
import os
import cv2
import pandas as pd
import numpy as np
import math as m

def LN2DUploadTo(instance, filename):
    return filename

class LN2DMixin(PrefixPtr, Unique):
    # Parameter
    lnmax = models.PositiveSmallIntegerField(verbose_name='LNMax', default=50)
    ntrials = models.PositiveIntegerField(verbose_name='NTrials', default=1000000)
    randseed = models.PositiveIntegerField(verbose_name='RandSeed', default=123456789)
    # Feature
    areafraction = models.FloatField(verbose_name='AreaFraction', blank=True, null=True)
    ln2d_tot = models.PositiveIntegerField(verbose_name='LN2D_tot', blank=True, null=True)
    ln2d_ave = models.FloatField(verbose_name='LN2D_ave', blank=True, null=True)
    ln2d_var = models.FloatField(verbose_name='LN2D_var', blank=True, null=True)
    ln2dr_tot = models.PositiveIntegerField(verbose_name='LN2DR_tot', blank=True, null=True)
    ln2dr_ave = models.FloatField(verbose_name='LN2DR_ave', blank=True, null=True)
    ln2dr_var = models.FloatField(verbose_name='LN2DR_var', blank=True, null=True)
    # File
    file = models.FileField(verbose_name='Measure file', upload_to=ModelUploadTo, blank=True, null=True)

    def measure_ln2d(self, conts, width, height, ps):
        freq = np.zeros((2, self.lnmax), dtype=np.uint32)
        ln2d = MPLn23d.ln2d_new(1)
        ln2d.seed = self.randseed
        sx = width * ps
        sy = height * ps
        sid = ln2d.add_sec(len(conts), sx, sy)
        for cont in conts:
            mom = cv2.moments(cont)
            if mom['m00'] != 0:
                x = mom['m10'] / mom['m00'] * ps
                y = mom['m01'] / mom['m00'] * ps
                area = cv2.contourArea(cont)
                r = m.sqrt(area / m.pi) * ps
                ln2d.add_gc(sid, x, y, r)
        ln2d.measure_gc(freq[0])
        ln2d.measure_random(freq[1], self.ntrials)
        self.areafraction = ln2d.area_fraction()
        tot, ave, var, rfreq0 = self.statistics(freq[0])
        self.ln2d_tot = tot
        self.ln2d_ave = ave
        self.ln2d_var = var
        tot, ave, var, rfreq1 = self.statistics(freq[1])
        self.ln2dr_tot = tot
        self.ln2dr_ave = ave
        self.ln2dr_var = var
        ln = np.arange(self.lnmax)
        df = pd.DataFrame([ln, freq[0], freq[1], rfreq0, rfreq1],
                          index=['LN', 'LN2D', 'LN2DR', 'LN2D_RF', 'LN2DR_RF']).T
        self.save_csv(df)

    def statistics(self, freq):
        tot = np.sum(freq)
        rfreq = np.array(freq, dtype=np.float64) / tot
        length = np.arange(len(freq))
        ave = np.sum(length * rfreq)
        var = np.sum(np.power(length - ave, 2) * rfreq)
        return tot, ave, var, rfreq

    def save_csv(self, df):
        buf = BytesIO()
        df.to_csv(buf, index=False, mode="wb", encoding="UTF-8")
        self.file.save('LN2D.csv', buf, save=False)
        buf.close()

    def read_csv(self):
        with self.file.open('r') as f:
            return pd.read_csv(f)
        return None

    def poisson_prob(self, a, b, lnmax):
        x = np.arange(b - 1 + 0.1, lnmax, 0.1)
        y = np.zeros(x.size, dtype=np.float64)
        for i in range(x.size):
            y[i] = m.pow(a, x[i] - b) / m.gamma(x[i] - b + 1) * m.exp(-a)
        return [x, y]

    def ln2d_ab(self):
        af = self.areafraction
        p, q, r, s = 6.1919, 5.8194, 5.1655, 5.7928
        a = p * (m.exp(-q * af) - 1) + 7
        b = r * (1 - m.exp(-s * af)) + 1
        return a, b, a + b

    def ln2d_prob(self, lnmax):
        a, b, tmp = self.ln2d_ab()
        return self.poisson_prob(a, b, lnmax)

    def ln2dr_ab(self):
        af = self.areafraction
        p, q = 5.8277, 6.0755
        a = p * (m.exp(-q * af) - 1) + 7
        b = p * (1 - m.exp(-q * af))
        return a, b, a + b

    def ln2dr_prob(self, lnmax):
        a, b, tmp = self.ln2dr_ab()
        return self.poisson_prob(a, b, lnmax)

    def draw_contours(self, conts, img):
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        for cont in conts:
            mom = cv2.moments(cont)
            if mom['m00'] != 0:
                x = int(mom['m10'] / mom['m00'])
                y = int(mom['m01'] / mom['m00'])
                cv2.line(img, (x, y - 3), (x, y + 3), (0, 0, 255))
                cv2.line(img, (x - 3, y), (x + 3, y), (0, 0, 255))
        cv2.drawContours(img, conts, -1, (255, 255, 0), 1)
        return img

    def feature(self):
        if self.status or self.upper.status or self.upper.upper.status or self.upper.upper.upper.status:
            return {}
        else:
            upper_feature = self.upper.feature()
            prefix = self.prefix_display()
            return {
                **upper_feature,
                'Model': self.__class__.__name__,
                'Model_id': self.id,
                'Category': 'structure',
                prefix+'_ln2d_ave': self.ln2d_ave,
                prefix+'_ln2d_var': self.ln2d_var,
                prefix+'_ln2dr_ave': self.ln2dr_ave,
                prefix+'_ln2dr_var': self.ln2dr_var
            }

    class Meta:
        abstract = True

class LN2D(Created, Updated, Remote, LN2DMixin):
    upper = models.ForeignKey(Filter, verbose_name='Filter', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('image:ln2d_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('image:ln2d_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('image:ln2d_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('image:ln2d_delete', kwargs={'pk': self.id})

    # def basename(self):
    #     return os.path.basename(self.file.name)
    #
    # def recent_updated_at(self):
    #     updated_at = self.upper.recent_updated_at()
    #     if self.updated_at > updated_at:
    #         updated_at = self.updated_at
    #     return updated_at

    def upper_updated(self):
        return self.updated_at < self.upper.recent_updated_at()

    def measure(self):
        cvimg = self.upper.check_read_img()
        if cvimg.ndim != 2:
            cvimg = cv2.cvtColor(cvimg, cv2.COLOR_BGR2GRAY)
        conts, hier = cv2.findContours(cvimg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        self.measure_ln2d(conts, cvimg.shape[1], cvimg.shape[0], self.upper.pixelsize)

    def get_image(self, **kwargs):
        cvimg = self.upper.check_read_img()
        if cvimg.ndim != 2:
            cvimg = cv2.cvtColor(cvimg, cv2.COLOR_BGR2GRAY)
        conts, hier = cv2.findContours(cvimg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        orgimg = self.upper.upper.read_img()
        orgimg, kwargs = self.upper.procimg(orgimg, sizeprocess=True)
        return cv2PIL(self.draw_contours(conts, orgimg))

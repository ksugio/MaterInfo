from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from project.models import Created, Updated, Remote, PrefixPtr, ModelUploadTo
from .filter import Filter
from io import BytesIO
import os
import numpy as np
import cv2
import pandas as pd
import math as m

def SizeUploadTo(instance, filename):
    return filename

class Size(Created, Updated, Remote, PrefixPtr):
    upper = models.ForeignKey(Filter, verbose_name='Filter', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    mindia = models.FloatField(verbose_name='Minimum Diameter', default=1.0)
    # AreaFraction and NumberDensity
    areafraction = models.FloatField(verbose_name='AreaFraction', blank=True, null=True)
    numberdensity = models.FloatField(verbose_name='NumberDensity', blank=True, null=True)
    # Diameter
    diameter_mean = models.FloatField(verbose_name='Diameter_mean', blank=True, null=True)
    diameter_std = models.FloatField(verbose_name='Diameter_std', blank=True, null=True)
    diameter_min = models.FloatField(verbose_name='Diameter_min', blank=True, null=True)
    diameter_median = models.FloatField(verbose_name='Diameter_median', blank=True, null=True)
    diameter_max = models.FloatField(verbose_name='Diameter_max', blank=True, null=True)
    # LongSide
    longside_mean = models.FloatField(verbose_name='LongSide_mean', blank=True, null=True)
    longside_std = models.FloatField(verbose_name='LongSide_std', blank=True, null=True)
    longside_min = models.FloatField(verbose_name='LongSide_min', blank=True, null=True)
    longside_median = models.FloatField(verbose_name='LongSide_median', blank=True, null=True)
    longside_max = models.FloatField(verbose_name='LongSide_max', blank=True, null=True)
    # NarrowSide
    narrowside_mean = models.FloatField(verbose_name='NarrowSide_mean', blank=True, null=True)
    narrowside_std = models.FloatField(verbose_name='NarrowSide_std', blank=True, null=True)
    narrowside_min = models.FloatField(verbose_name='NarrowSide_min', blank=True, null=True)
    narrowside_median = models.FloatField(verbose_name='NarrowSide_median', blank=True, null=True)
    narrowside_max = models.FloatField(verbose_name='NarrowSide_max', blank=True, null=True)
    # AspectRatio
    aspectratio_mean = models.FloatField(verbose_name='AspectRatio_mean', blank=True, null=True)
    aspectratio_std = models.FloatField(verbose_name='AspectRatio_std', blank=True, null=True)
    aspectratio_min = models.FloatField(verbose_name='AspectRatio_min', blank=True, null=True)
    aspectratio_median = models.FloatField(verbose_name='AspectRatio_median', blank=True, null=True)
    aspectratio_max = models.FloatField(verbose_name='AspectRatio_max', blank=True, null=True)
    # Circularity
    circularity_mean = models.FloatField(verbose_name='Circularity_mean', blank=True, null=True)
    circularity_std = models.FloatField(verbose_name='Circularity_std', blank=True, null=True)
    circularity_min = models.FloatField(verbose_name='Circularity_min', blank=True, null=True)
    circularity_median = models.FloatField(verbose_name='Circularity_median', blank=True, null=True)
    circularity_max = models.FloatField(verbose_name='Circularity_max', blank=True, null=True)
    # Angle
    angle_mean = models.FloatField(verbose_name='Angle_mean', blank=True, null=True)
    angle_std = models.FloatField(verbose_name='Angle_std', blank=True, null=True)
    angle_min = models.FloatField(verbose_name='Angle_min', blank=True, null=True)
    angle_median = models.FloatField(verbose_name='Angle_median', blank=True, null=True)
    angle_max = models.FloatField(verbose_name='Angle_max', blank=True, null=True)
    # File
    file = models.FileField(verbose_name='Measure file', upload_to=ModelUploadTo, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('image:size_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('image:size_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('image:size_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('image:size_delete', kwargs={'pk': self.id})

    def pathname(self):
        return '%s/%s/%s' % (self.upper.upper.upper, self.upper.upper, self.upper)

    def basename(self):
        return os.path.basename(self.file.name)

    def recent_updated_at(self):
        updated_at = self.upper.recent_updated_at()
        if self.updated_at > updated_at:
            updated_at = self.updated_at
        return updated_at

    def save_csv(self, df):
        buf = BytesIO()
        df.to_csv(buf, index=False, mode="wb", encoding="UTF-8")
        self.file.save('Size.csv', buf, save=False)
        buf.close()

    def read_csv(self):
        with self.file.open('r') as f:
            return pd.read_csv(f)
        return None

    def contours(self):
        procimg = self.upper.check_read_img()
        if procimg.ndim != 2:
            return procimg, None
        conts, hier = cv2.findContours(procimg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        return procimg, conts

    def measure(self):
        procimg, conts = self.contours()
        if conts is None:
            return
        ps = self.upper.pixelsize
        data = []
        totarea = 0.0
        for cont in conts:
            mom = cv2.moments(cont)
            if mom['m00'] != 0:
                x = mom['m10'] / mom['m00'] * ps
                y = mom['m01'] / mom['m00'] * ps
                area = cv2.contourArea(cont)
                dia = 2.0 * m.sqrt(area / m.pi) * ps
                pos, size, ang = cv2.minAreaRect(cont)
                per = cv2.arcLength(cont, True)
                cir = 4.0 * m.pi * area / (per * per)
                totarea = totarea + area
                if size[0] >= size[1]:
                    ls = size[0] * ps
                    ns = size[1] * ps
                    asp = size[1] / size[0]
                    ang += 90
                else:
                    ls = size[1] * ps
                    ns = size[0] * ps
                    asp = size[0] / size[1]
                if ang >= 180:
                    ang -= 180
                if dia >= self.mindia:
                    data.append([x, y, dia, ls, ns, asp, cir, ang])
        header = ['X', 'Y', 'Diameter', 'LongSide', 'NarrowSide', 'AspectRatio', 'Circularity', 'Angle']
        df = pd.DataFrame(data, dtype='float64', columns=header)
        imgarea = procimg.shape[1] * procimg.shape[0]
        self.areafraction = totarea / imgarea
        self.numberdensity = len(data) / (imgarea * ps * ps)
        # Diameter
        self.diameter_mean = df['Diameter'].mean()
        self.diameter_std = df['Diameter'].std()
        self.diameter_min = df['Diameter'].min()
        self.diameter_median = df['Diameter'].median()
        self.diameter_max = df['Diameter'].max()
        # LongSide
        self.longside_mean = df['LongSide'].mean()
        self.longside_std = df['LongSide'].std()
        self.longside_min = df['LongSide'].min()
        self.longside_median = df['LongSide'].median()
        self.longside_max = df['LongSide'].max()
        # NarrowSide
        self.narrowside_mean = df['NarrowSide'].mean()
        self.narrowside_std = df['NarrowSide'].std()
        self.narrowside_min = df['NarrowSide'].min()
        self.narrowside_median = df['NarrowSide'].median()
        self.narrowside_max = df['NarrowSide'].max()
        # AspectRatio
        self.aspectratio_mean = df['AspectRatio'].mean()
        self.aspectratio_std = df['AspectRatio'].std()
        self.aspectratio_min = df['AspectRatio'].min()
        self.aspectratio_median = df['AspectRatio'].median()
        self.aspectratio_max = df['AspectRatio'].max()
        # Circularity
        self.circularity_mean = df['Circularity'].mean()
        self.circularity_std = df['Circularity'].std()
        self.circularity_min = df['Circularity'].min()
        self.circularity_median = df['Circularity'].median()
        self.circularity_max = df['Circularity'].max()
        # Angle
        self.angle_mean = df['Angle'].mean()
        self.angle_std = df['Angle'].std()
        self.angle_min = df['Angle'].min()
        self.angle_median = df['Angle'].median()
        self.angle_max = df['Angle'].max()
        # Save DataFrame
        self.save_csv(df)

    def contsimg(self, gc, bb):
        procimg, conts = self.contours()
        if conts is None:
            return
        orgimg = self.upper.upper.read_img()
        orgimg, kwargs = self.upper.procimg(orgimg, sizeprocess=True)
        if len(orgimg.shape) == 2:
            orgimg = cv2.cvtColor(orgimg, cv2.COLOR_GRAY2BGR)
        if gc > 0:
            for cont in conts:
                mom = cv2.moments(cont)
                if mom['m00'] != 0:
                    x = int(mom['m10'] / mom['m00'])
                    y = int(mom['m01'] / mom['m00'])
                    cv2.line(orgimg, (x, y - 3), (x, y + 3), (0, 0, 255))
                    cv2.line(orgimg, (x - 3, y), (x + 3, y), (0, 0, 255))
        if bb > 0:
            for cont in conts:
                rect = cv2.minAreaRect(cont)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(orgimg, [box], 0, (255, 0, 0), 1)
        cv2.drawContours(orgimg, conts, -1, (255, 255, 0), 1)
        return orgimg

    def upper_updated(self):
        return self.updated_at < self.upper.recent_updated_at()

    def upper_updated_measure(self):
        if self.upper_updated():
            self.measure()
            self.save()
            return True
        else:
            return False

    def feature(self):
        if self.status or self.upper.status or self.upper.upper.status or self.upper.upper.upper.status:
            return {}
        else:
            prefix = self.prefix_display()
            return {
                'Project_id': self.upper.upper.upper.upper.id,
                'Project_title': self.upper.upper.upper.upper.title,
                'Sample_id': self.upper.upper.upper.id,
                'Sample_title': self.upper.upper.upper.title,
                'Image_id': self.upper.upper.id,
                'Image_title': self.upper.upper.title,
                'Image_Filter_id': self.upper.entity_id(),
                'Model': self.__class__.__name__,
                'Model_id': self.id,
                'Category': 'structure',
                prefix+'_areafraction': self.areafraction,
                prefix+'_numberdensity': self.numberdensity,
                prefix+'_diameter_mean': self.diameter_mean,
                prefix+'_diameter_std': self.diameter_std,
                prefix+'_diameter_min': self.diameter_min,
                prefix+'_diameter_median': self.diameter_median,
                prefix+'_diameter_max': self.diameter_max,
                prefix+'_longside_mean': self.longside_mean,
                prefix+'_longside_std': self.longside_std,
                prefix+'_longside_min': self.longside_min,
                prefix+'_longside_median': self.longside_median,
                prefix+'_longside_max': self.longside_max,
                prefix+'_narrowside_mean': self.narrowside_mean,
                prefix+'_narrowside_std': self.narrowside_std,
                prefix+'_narrowside_min': self.narrowside_min,
                prefix+'_narrowside_median': self.narrowside_median,
                prefix+'_narrowside_max': self.narrowside_max,
                prefix+'_aspectratio_mean': self.aspectratio_mean,
                prefix+'_aspectratio_std': self.aspectratio_std,
                prefix+'_aspectratio_min': self.aspectratio_min,
                prefix+'_aspectratio_median': self.aspectratio_median,
                prefix+'_aspectratio_max': self.aspectratio_max,
                prefix+'_circularity_mean': self.circularity_mean,
                prefix+'_circularity_std': self.circularity_std,
                prefix+'_circularity_min': self.circularity_min,
                prefix+'_circularity_median': self.circularity_median,
                prefix+'_circularity_max': self.circularity_max,
                prefix+'_angle_mean': self.angle_mean,
                prefix+'_angle_std': self.angle_std,
                prefix+'_angle_min': self.angle_min,
                prefix+'_angle_median': self.angle_median,
                prefix+'_angle_max': self.angle_max
            }

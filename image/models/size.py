from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, PrefixPtr, ModelUploadTo, Unique
from .filter import Filter
from io import BytesIO
import numpy as np
import cv2
import pandas as pd
import math as m
import json

def SizeUploadTo(instance, filename):
    return filename

class SizeMixin(PrefixPtr, Unique):
    mindia = models.FloatField(verbose_name='Minimum Diameter', default=1.0)
    roiarea = models.FloatField(verbose_name='ROI Area (px)', blank=True, null=True)
    results = models.TextField(verbose_name='JSON Results', blank=True)
    file = models.FileField(verbose_name='Measure file', upload_to=ModelUploadTo, blank=True, null=True)

    def measure_size(self, conts, imgarea, ps):
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
        if self.roiarea:
            imgarea = self.roiarea
        results = {
            'areafraction': totarea / imgarea,
            'numberdensity': len(data) / (imgarea * ps * ps),
            # Diameter
            'diameter_mean': df['Diameter'].mean(),
            'diameter_std': df['Diameter'].std(),
            'diameter_min': df['Diameter'].min(),
            'diameter_median': df['Diameter'].median(),
            'diameter_max': df['Diameter'].max(),
            # LongSide
            'longside_mean': df['LongSide'].mean(),
            'longside_std': df['LongSide'].std(),
            'longside_min': df['LongSide'].min(),
            'longside_median': df['LongSide'].median(),
            'longside_max': df['LongSide'].max(),
            # NarrowSide
            'narrowside_mean': df['NarrowSide'].mean(),
            'narrowside_std': df['NarrowSide'].std(),
            'narrowside_min': df['NarrowSide'].min(),
            'narrowside_median': df['NarrowSide'].median(),
            'narrowside_max': df['NarrowSide'].max(),
            # AspectRatio
            'aspectratio_mean': df['AspectRatio'].mean(),
            'aspectratio_std': df['AspectRatio'].std(),
            'aspectratio_min': df['AspectRatio'].min(),
            'aspectratio_median': df['AspectRatio'].median(),
            'aspectratio_max': df['AspectRatio'].max(),
            # Circularity
            'circularity_mean': df['Circularity'].mean(),
            'circularity_std': df['Circularity'].std(),
            'circularity_min': df['Circularity'].min(),
            'circularity_median': df['Circularity'].median(),
            'circularity_max': df['Circularity'].max(),
            # Angle
            'angle_mean': df['Angle'].mean(),
            'angle_std': df['Angle'].std(),
            'angle_min': df['Angle'].min(),
            'angle_median': df['Angle'].median(),
            'angle_max': df['Angle'].max()
        }
        self.save_csv(df)
        self.results = json.dumps(results)

    def save_csv(self, df):
        buf = BytesIO()
        df.to_csv(buf, index=False, mode="wb", encoding="UTF-8")
        self.file.save('Size.csv', buf, save=False)
        buf.close()

    def read_csv(self):
        with self.file.open('r') as f:
            return pd.read_csv(f)
        return None

    def draw_contours(self, conts, img, gc, bb):
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        if gc > 0:
            for cont in conts:
                mom = cv2.moments(cont)
                if mom['m00'] != 0:
                    x = int(mom['m10'] / mom['m00'])
                    y = int(mom['m01'] / mom['m00'])
                    cv2.line(img, (x, y - 3), (x, y + 3), (0, 0, 255))
                    cv2.line(img, (x - 3, y), (x + 3, y), (0, 0, 255))
        if bb > 0:
            for cont in conts:
                rect = cv2.minAreaRect(cont)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(img, [box], 0, (255, 0, 0), 1)
        cv2.drawContours(img, conts, -1, (255, 255, 0), 1)
        return img

    def feature(self):
        if self.status or self.upper.status or self.upper.upper.status or self.upper.upper.upper.status:
            return {}
        elif self.results:
            upper_feature = self.upper.feature()
            prefix = self.prefix_display()
            results = json.loads(self.results)
            return {
                **upper_feature,
                'Model': self.__class__.__name__,
                'Model_id': self.id,
                'Category': 'structure',
                prefix+'_areafraction': results['areafraction'],
                prefix+'_numberdensity': results['numberdensity'],
                prefix+'_diameter_mean': results['diameter_mean'],
                prefix+'_diameter_std': results['diameter_std'],
                prefix+'_diameter_min': results['diameter_min'],
                prefix+'_diameter_median': results['diameter_median'],
                prefix+'_diameter_max': results['diameter_max'],
                prefix+'_longside_mean': results['longside_mean'],
                prefix+'_longside_std': results['longside_std'],
                prefix+'_longside_min': results['longside_min'],
                prefix+'_longside_median': results['longside_median'],
                prefix+'_longside_max': results['longside_max'],
                prefix+'_narrowside_mean': results['narrowside_mean'],
                prefix+'_narrowside_std': results['narrowside_std'],
                prefix+'_narrowside_min': results['narrowside_min'],
                prefix+'_narrowside_median': results['narrowside_median'],
                prefix+'_narrowside_max': results['narrowside_max'],
                prefix+'_aspectratio_mean': results['aspectratio_mean'],
                prefix+'_aspectratio_std': results['aspectratio_std'],
                prefix+'_aspectratio_min': results['aspectratio_min'],
                prefix+'_aspectratio_median': results['aspectratio_median'],
                prefix+'_aspectratio_max': results['aspectratio_max'],
                prefix+'_circularity_mean': results['circularity_mean'],
                prefix+'_circularity_std': results['circularity_std'],
                prefix+'_circularity_min': results['circularity_min'],
                prefix+'_circularity_median': results['circularity_median'],
                prefix+'_circularity_max': results['circularity_max'],
                prefix+'_angle_mean': results['angle_mean'],
                prefix+'_angle_std': results['angle_std'],
                prefix+'_angle_min': results['angle_min'],
                prefix+'_angle_median': results['angle_median'],
                prefix+'_angle_max': results['angle_max']
            }
        else:
            return {}

    class Meta:
        abstract = True

class Size(Created, Updated, Remote, SizeMixin):
    upper = models.ForeignKey(Filter, verbose_name='Filter', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)

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

    def get_apiupdate_url(self):
        return reverse('image:api_size_update', kwargs={'pk': self.id})

    # def basename(self):
    #     return os.path.basename(self.file.name)

    # def recent_updated_at(self):
    #     updated_at = self.upper.recent_updated_at()
    #     if self.updated_at > updated_at:
    #         updated_at = self.updated_at
    #     return updated_at

    def upper_updated(self):
        return self.updated_at < self.upper.recent_updated_at()

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
        imgarea = procimg.shape[1] * procimg.shape[0]
        self.measure_size(conts, imgarea, self.upper.pixelsize)

    def contsimg(self, gc, bb):
        procimg, conts = self.contours()
        if conts is None:
            return
        orgimg = self.upper.upper.read_img()
        orgimg, kwargs = self.upper.procimg(orgimg, sizeprocess=True)
        return self.draw_contours(conts, orgimg, gc, bb)

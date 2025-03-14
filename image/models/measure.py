from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, PrefixPtr
from .image import Image
import json
import math as m
import pandas as pd
import numpy as np
import cv2

def Distance(pt1, pt2):
    dx = pt2[0] - pt1[0]
    dy = pt2[1] - pt1[1]
    return m.sqrt(dx * dx + dy * dy)

class Measure(Created, Updated, Remote, PrefixPtr):
    upper = models.ForeignKey(Image, verbose_name='Image', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    TypeChoices = ((0, 'Length'), (1, 'Angle'), (2, 'Area'))
    type = models.PositiveSmallIntegerField(verbose_name='Type', choices=TypeChoices, default=0)
    data = models.TextField(verbose_name='Data', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('image:measure_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('image:measure_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('image:measure_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('image:measure_delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('image:api_measure_update', kwargs={'pk': self.id})

    def get_df(self):
        if not self.data:
            return None
        if self.type == 0:
            items = []
            for pts in json.loads(self.data):
                dis = Distance(pts[0], pts[1])
                length = dis * self.upper.pixelsize()
                items.append([pts[0][0], pts[0][1], pts[1][0], pts[1][1], dis, length])
            return pd.DataFrame(items, columns=['p1x', 'p1y', 'p2x', 'p2y', 'pixel', 'length'])
        elif self.type == 1:
            items = []
            for pts in json.loads(self.data):
                v1x = pts[0][0] - pts[1][0]
                v1y = pts[0][1] - pts[1][1]
                v2x = pts[2][0] - pts[1][0]
                v2y = pts[2][1] - pts[1][1]
                dot = v1x * v2x + v1y * v2y
                d1 = Distance(pts[0], pts[1])
                d2 = Distance(pts[1], pts[2])
                angle = m.acos(dot / (d1 * d2)) / m.pi * 180
                items.append([pts[0][0], pts[0][1], pts[1][0], pts[1][1], pts[2][0], pts[2][1], angle])
            return pd.DataFrame(items, columns=['p1x', 'p1y', 'p2x', 'p2y', 'p3x', 'p3y', 'angle'])
        elif self.type == 2:
            items = []
            for pts in json.loads(self.data):
                ps = self.upper.pixelsize()
                cont = np.array(pts, dtype=np.int32)
                mom = cv2.moments(cont)
                x = mom['m10'] / mom['m00'] * ps
                y = mom['m01'] / mom['m00'] * ps
                area = cv2.contourArea(cont)
                psarea = area * ps * ps
                items.append([x, y, area, psarea])
            return pd.DataFrame(items, columns=['cx', 'cy', 'pixel', 'area'])

    def get_desc(self):
        df = self.get_df()
        if df is None:
            return None
        if self.type == 0:
            describe = df['length'].describe()
        elif self.type == 1:
            describe = df['angle'].describe()
        elif self.type == 2:
            describe = df['area'].describe()
        if '50%' in describe:
            describe['median'] = describe['50%']
        return describe

    def feature(self):
        if self.status or self.upper.status or self.upper.upper.status:
            return {}
        elif self.data:
            prefix = self.prefix_display()
            if self.type == 0:
                type = '_length'
            elif self.type == 1:
                type =  '_angle'
            elif self.type == 2:
                type = '_area'
            describe = self.get_desc()
            return {
                'Project_id': self.upper.upper.upper.id,
                'Project_title': self.upper.upper.upper.title,
                'Sample_id': self.upper.upper.id,
                'Sample_title': self.upper.upper.title,
                'Image_id': self.upper.id,
                'Image_title': self.upper.title,
                'Model': self.__class__.__name__,
                'Model_id': self.id,
                'Category': 'structure',
                prefix + type + '_mean': describe['mean'],
                prefix + type + '_std': describe['std'],
                prefix + type + '_min': describe['min'],
                prefix + type + '_median': describe['median'],
                prefix + type + '_max': describe['max'],
            }

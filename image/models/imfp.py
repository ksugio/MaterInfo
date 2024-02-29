from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, PrefixPtr, ModelUploadTo
from .filter import Filter
from io import BytesIO
import MPImfp
import os
import pandas as pd
import numpy as np
import math as m

def IMFPUploadTo(instance, filename):
    return filename

class IMFP(Created, Updated, Remote, PrefixPtr):
    upper = models.ForeignKey(Filter, verbose_name='Filter', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    BarrierChoices = ((0, 'White'), (2, 'Black'))
    barrier = models.PositiveSmallIntegerField(verbose_name='Barrier', choices=BarrierChoices, default=0)
    nclass = models.PositiveSmallIntegerField(verbose_name='NClass', default=5000)
    ntrials = models.PositiveIntegerField(verbose_name='NTrials', default=1000000)
    randseed = models.PositiveIntegerField(verbose_name='RandSeed', default=123456789)
    # Feature
    single_ave = models.FloatField(verbose_name='Single_ave', blank=True, null=True)
    single_std = models.FloatField(verbose_name='Single_std', blank=True, null=True)
    double_ave = models.FloatField(verbose_name='Double_ave', blank=True, null=True)
    double_std = models.FloatField(verbose_name='Double_std', blank=True, null=True)
    # File
    file = models.FileField(verbose_name='Measure file', upload_to=ModelUploadTo, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('image:imfp_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('image:imfp_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('image:imfp_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('image:imfp_delete', kwargs={'pk': self.id})

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
        self.file.save('IMFP.csv', buf, save=False)
        buf.close()

    def read_csv(self):
        with self.file.open('r') as f:
            return pd.read_csv(f)
        return None

    def measure(self):
        cvimg = self.upper.check_read_img()
        if cvimg.ndim != 2:
            return
        freq = np.zeros((2, self.nclass), dtype=np.uint32)
        if self.barrier == 1:
            barrier = 0
        else:
            barrier = 255
        MPImfp.measure(cvimg, barrier, freq[0], 1.0, self.ntrials, self.randseed, 0)
        MPImfp.measure(cvimg, barrier, freq[1], 1.0, self.ntrials, self.randseed, 1)
        tot, ave, std, rfreq0 = self.statistics(freq[0])
        self.single_ave = ave
        self.single_std = std
        tot, ave, std, rfreq1 = self.statistics(freq[1])
        self.double_ave = ave
        self.double_std = std
        # Save DataFrame
        nclass = np.arange(self.nclass)
        df = pd.DataFrame([nclass, freq[0], freq[1], rfreq0, rfreq1],
                          index=['NClass', 'Single', 'Double', 'Single_RF', 'Double_RF']).T
        self.save_csv(df)

    def statistics(self, freq):
        tot = np.sum(freq)
        rfreq = np.array(freq, dtype=np.float64) / tot
        length = np.arange(len(freq)) * self.upper.pixelsize
        ave = np.sum(length * rfreq)
        var = np.sum(np.power(length - ave, 2) * rfreq)
        std = m.sqrt(var)
        return tot, ave, std, rfreq

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
                prefix+'_single_ave': self.single_ave,
                prefix+'_single_std': self.single_std,
                prefix+'_double_ave': self.double_ave,
                prefix+'_double_std': self.double_std
            }

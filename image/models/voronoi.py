from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, PrefixPtr, ModelUploadTo, Unique
from .filter import Filter, cv2PIL
from io import BytesIO
import cv2
import pandas as pd
import json

class VoronoiMixin(PrefixPtr, Unique):
    results = models.TextField(verbose_name='JSON Results', blank=True)
    file = models.FileField(verbose_name='Measure file', upload_to=ModelUploadTo, blank=True, null=True)

    def get_voronoi(self, conts, width, height):
        subdiv = cv2.Subdiv2D((0, 0, width, height))
        for cont in conts:
            mom = cv2.moments(cont)
            if mom['m00'] != 0:
                x = mom['m10'] / mom['m00']
                y = mom['m01'] / mom['m00']
                subdiv.insert((x, y))
        return subdiv.getVoronoiFacetList([])

    def valid_indexes(self, width, height, facets):
        indexes = []
        for i, facet in enumerate(facets):
            for pt in facet:
                if pt[0] < 0 or pt[0] >= width or pt[1] < 0 or pt[1] >= height:
                    break
            else:
                indexes.append(i)
        return indexes

    def measure_voronoi(self, conts, width, height, ps):
        facets, centers = self.get_voronoi(conts, width, height)
        vinds = self.valid_indexes(width, height, facets)
        data = []
        for id in vinds:
            area = cv2.contourArea(facets[id]) * ps * ps
            data.append([centers[id][0], centers[id][1], len(facets[id]), area])
        df = pd.DataFrame(data, columns=['X', 'Y', 'VFacet', 'VArea'])
        self.save_csv(df)
        df = df.describe()
        df.index = ['count', 'mean', 'std', 'min', 'quarter', 'median', 'threequarters', 'max']
        df = df.drop(['quarter', 'threequarters'], axis=0)
        results = {
            'VFacet': df['VFacet'].to_dict(),
            'VArea': df['VArea'].to_dict()
        }
        self.results = json.dumps(results)

    def save_csv(self, df):
        buf = BytesIO()
        df.to_csv(buf, index=False, mode="wb", encoding="UTF-8")
        self.file.save('Voronoi.csv', buf, save=False)
        buf.close()

    def read_csv(self):
        with self.file.open('r') as f:
            return pd.read_csv(f)
        return None

    def draw_voronoi(self, conts, width, height, img):
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        facets, centers = self.get_voronoi(conts, width, height)
        vinds = self.valid_indexes(width, height, facets)
        cv2.polylines(img, [f.astype(int) for f in facets], True, (255, 255, 0), thickness=1)
        for id in vinds:
            x = int(centers[id][0])
            y = int(centers[id][1])
            cv2.line(img, (x, y - 3), (x, y + 3), (0, 0, 255))
            cv2.line(img, (x - 3, y), (x + 3, y), (0, 0, 255))
        return img

    def feature(self):
        if self.status or self.upper.status or self.upper.upper.status or self.upper.upper.upper.status:
            return {}
        else:
            upper_feature = self.upper.feature()
            prefix = self.prefix_display()
            results = json.loads(self.results)
            return {
                **upper_feature,
                'Model': self.__class__.__name__,
                'Model_id': self.id,
                'Category': 'structure',
                prefix+'_vfacet_mean': results['VFacet']['mean'],
                prefix+'_vfacet_std': results['VFacet']['std'],
                prefix+'_vfacet_min': results['VFacet']['min'],
                prefix+'_vfacet_median': results['VFacet']['median'],
                prefix+'_vfacet_max': results['VFacet']['max'],
                prefix+'_varea_mean': results['VArea']['mean'],
                prefix+'_varea_std': results['VArea']['std'],
                prefix+'_varea_min': results['VArea']['min'],
                prefix+'_varea_median': results['VArea']['median'],
                prefix+'_varea_max': results['VArea']['max'],
            }

    class Meta:
        abstract = True

class Voronoi(Created, Updated, Remote, VoronoiMixin):
    upper = models.ForeignKey(Filter, verbose_name='Filter', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('image:voronoi_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('image:voronoi_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('image:voronoi_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('image:voronoi_delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('image:api_voronoi_update', kwargs={'pk': self.id})

    def upper_updated(self):
        return self.updated_at < self.upper.recent_updated_at()

    def measure(self):
        cvimg = self.upper.check_read_img()
        if cvimg.ndim != 2:
            cvimg = cv2.cvtColor(cvimg, cv2.COLOR_BGR2GRAY)
        conts, hier = cv2.findContours(cvimg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        self.measure_voronoi(conts, cvimg.shape[1], cvimg.shape[0], self.upper.pixelsize)

    def get_image(self, **kwargs):
        cvimg = self.upper.check_read_img()
        if cvimg.ndim != 2:
            cvimg = cv2.cvtColor(cvimg, cv2.COLOR_BGR2GRAY)
        conts, hier = cv2.findContours(cvimg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if kwargs['type'] == 0:
            img = self.draw_voronoi(conts, cvimg.shape[1], cvimg.shape[0], cvimg)
        elif kwargs['type'] == 1:
            orgimg = self.upper.upper.read_img()
            orgimg, _ = self.upper.procimg(orgimg, sizeprocess=True)
            img = self.draw_voronoi(conts, cvimg.shape[1], cvimg.shape[0], orgimg)
        pilimg = cv2PIL(img)
        return pilimg

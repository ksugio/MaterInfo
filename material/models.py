from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, ModelUploadTo, PrefixPtr
from sample.models import Sample
import pandas as pd
import os

def MaterialUploadTo(instance, filename):
    return filename

def AtomicWeight(element):
    weight = ((1, 1.00794), (2, 4.002602), (3, 6.941), (4, 9.012182), (5, 10.811),
              (6, 12.0107), (7, 14.0067), (8, 15.9994), (9, 18.9984032), (10, 20.1797),
              (11, 22.98976928), (12, 24.3050), (13, 26.9815386), (14, 28.0855), (15, 30.973762),
              (16, 32.065), (17, 35.453), (18, 39.948), (19, 39.0983), (20, 40.078),
              (21, 44.955912), (22, 47.867), (23, 50.9415), (24, 51.9961), (25, 54.938045),
              (26, 55.845), (27, 58.933195), (28, 58.6934), (29, 63.546), (30, 65.38),
              (31, 69.723), (32, 72.64), (33, 74.92160), (34, 78.96), (35, 79.904),
              (36, 83.798), (37, 85.4678), (38, 87.62), (39, 88.90585), (40, 91.224),
              (41, 92.90638), (42, 95.96), (43, 98.9063), (44, 101.07), (45, 102.90550),
              (46, 106.42), (47, 107.8682), (48, 112.411), (49, 114.818), (50, 118.710),
              (51, 121.760), (52, 127.60), (53, 126.90447), (54, 131.293), (55, 132.9054519),
              (56, 137.327), (57, 138.90547), (58, 140.116), (59, 140.90765), (60, 144.242),
              (61, 146.9151), (62, 150.36), (63, 151.964), (64, 157.25), (65, 158.92535),
              (66, 162.500), (67, 164.93032), (68, 167.259), (69, 168.93421), (70, 173.054),
              (71, 174.9668), (72, 178.49), (73, 180.94788), (74, 183.84), (75, 186.207),
              (76, 190.23), (77, 192.217), (78, 195.084), (79, 196.966569), (80, 200.59),
              (81, 204.3833), (82, 207.2), (83, 208.98040), (84, 208.9824), (85, 209.9871),
              (86, 222.0176), (87, 223.0197), (88, 226.0254), (89, 227.0278), (90, 232.03806),
              (91, 231.03588), (92, 238.02891), (93, 237.0482), (94, 244.0642),)
    for w in weight:
        if w[0] == element:
            return w[1]

class Material(Created, Updated, Remote, PrefixPtr):
    upper = models.ForeignKey(Sample, verbose_name='Sample', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    fraction = models.FloatField(verbose_name='Fraction', blank=True, null=True)
    file = models.FileField(verbose_name='File', upload_to=ModelUploadTo, blank=True)
    PercentInChoices = ((0, 'mass%'), (1, 'atom%'))
    percent_in = models.PositiveSmallIntegerField(verbose_name='Percent in', choices=PercentInChoices, default=0)
    template = models.BooleanField(verbose_name='Template', default=False)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('material:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('material:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('material:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('material:delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('material:api_update', kwargs={'pk': self.id})

    def basename(self):
        return os.path.basename(self.file.name)

    def recent_updated_at(self):
        updated_at = self.updated_at
        elements = Element.objects.filter(upper=self).order_by('element')
        for element in elements:
            if element.updated_at > updated_at:
                updated_at = element.updated_at
        return updated_at

    def composition(self):
        elements = Element.objects.filter(upper=self).order_by('element')
        if len(elements) == 0:
            return None
        tot = 0
        nc = 0
        z = []
        symbol = []
        atomw = []
        for elm in elements:
            z.append(elm.element)
            symbol.append(elm.symbol())
            atomw.append(AtomicWeight(elm.element))
            if elm.fraction is not None:
                tot = tot + elm.fraction
            else:
                nc = nc + 1
        if nc > 0:
            res = (100.0 - tot) / nc
        else:
            res = 0.0
        if self.percent_in == 0:
            massfrac = []
            for elm in elements:
                if elm.fraction is not None:
                    massfrac.append(elm.fraction)
                else:
                    massfrac.append(res)
            tot = 0
            for i in range(len(massfrac)):
                tot = tot + massfrac[i] / atomw[i]
            atomfrac = []
            for i in range(len(massfrac)):
                atomfrac.append(massfrac[i] / atomw[i] / tot * 100)
        elif self.percent_in == 1:
            atomfrac = []
            for elm in elements:
                if elm.fraction is not None:
                    atomfrac.append(elm.fraction)
                else:
                    atomfrac.append(res)
            tot = 0
            for i in range(len(atomfrac)):
                tot = tot + atomfrac[i] * atomw[i]
            massfrac = []
            for i in range(len(atomfrac)):
                massfrac.append(atomfrac[i] * atomw[i] / tot * 100)
        dic = dict(Title=symbol, AtomicWeight=atomw, MassPercent=massfrac, AtomPercent=atomfrac)
        return pd.DataFrame(data=dic, index=z)

    def feature(self):
        if self.status or self.upper.status:
            return {}
        else:
            upper_feature = self.upper.feature()
            comp = self.composition()
            if comp is None:
                return {}
            dic = {
                **upper_feature,
                'Model': self.__class__.__name__,
                'Model_id': self.id,
                'Category': 'process'
            }
            prefix = self.prefix_display()
            for ind in comp.index.values:
                title = comp.loc[ind]['Title']
                masskey = '%s_%s_massp' % (prefix, title)
                dic[masskey] = comp.loc[ind]['MassPercent']
                atomkey = '%s_%s_atomp' % (prefix, title)
                dic[atomkey] = comp.loc[ind]['AtomPercent']
            return dic

class Element(Updated, Remote):
    upper = models.ForeignKey(Material, verbose_name='Material', on_delete=models.CASCADE)
    TypeChoices = ((1, 'H'), (2, 'He'), (3, 'Li'), (4, 'Be'), (5, 'B'),
                   (6, 'C'), (7, 'N'), (8, 'O'), (9, 'F'), (10, 'Ne'),
                   (11, 'Na'), (12, 'Mg'), (13, 'Al'), (14, 'Si'), (15, 'P'),
                   (16, 'S'), (17, 'Cl'), (18, 'Ar'), (19, 'K'), (20, 'Ca'),
                   (21, 'Sc'), (22, 'Ti'), (23, 'V'), (24, 'Cr'), (25, 'Mn'),
                   (26, 'Fe'), (27, 'Co'), (28, 'Ni'), (29, 'Cu'), (30, 'Zn'),
                   (31, 'Ga'), (32, 'Ge'), (33, 'As'), (34, 'Se'), (35, 'Br'),
                   (36, 'Kr'), (37, 'Rb'), (38, 'Sr'), (39, 'Y'), (40, 'Zr'),
                   (41, 'Nb'), (42, 'Mo'), (43, 'Tc'), (44, 'Ru'), (45, 'Rh'),
                   (46, 'Pd'), (47, 'Ag'), (48, 'Cd'), (49, 'In'), (50, 'Sn'),
                   (51, 'Sb'), (52, 'Te'), (53, 'I'), (54, 'Xe'), (55, 'Cs'),
                   (56, 'Ba'), (57, 'La'), (58, 'Ce'), (59, 'Pr'), (60, 'Nd'),
                   (61, 'Pm'), (62, 'Sm'), (63, 'Eu'), (64, 'Gd'), (65, 'Tb'),
                   (66, 'Dy'), (67, 'Ho'), (68, 'Er'), (69, 'Tm'), (70, 'Yb'),
                   (71, 'Lu'), (72, 'Hf'), (73, 'Ta'), (74, 'W'), (75, 'Re'),
                   (76, 'Os'), (77, 'Ir'), (78, 'Pt'), (79, 'Au'), (80, 'Hg'),
                   (81, 'Tl'), (82, 'Pb'), (83, 'Bi'), (84, 'Po'), (85, 'At'),
                   (86, 'Rn'), (87, 'Fr'), (88, 'Ra'), (89, 'Ac'), (90, 'Th'),
                   (91, 'Pa'), (92, 'U'), (93, 'Np'), (94, 'Pu'))
    element = models.PositiveSmallIntegerField(verbose_name='Element', choices=TypeChoices)
    fraction = models.FloatField(verbose_name='Fraction', blank=True, null=True)

    def __str__(self):
        return self.symbol()

    def title(self):
        return '%s : %s' % (self.upper.title, self.symbol())

    def symbol(self):
        for item in self.TypeChoices:
            if item[0] == self.element:
                return item[1]

    def get_detail_url(self):
        return reverse('material:update', kwargs={'pk': self.upper.id})

    def get_update_url(self):
        return reverse('material:element_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('material:element_delete', kwargs={'pk': self.id})

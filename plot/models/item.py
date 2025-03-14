from django.db import models
from django.urls import reverse
from project.models import Updated, Remote
from .area import Area
from io import BytesIO
import requests
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ColorChoices = ((0, 'b'), (1, 'g'), (2, 'r'), (3, 'c'), (4, 'm'), (5, 'y'), (6, 'k'), (7, 'w'),
                (8, 'black'), (9, 'dimgray'), (10, 'dimgrey'), (11, 'gray'),
                (12, 'grey'), (13, 'darkgray'), (14, 'darkgrey'), (15, 'silver'),
                (16, 'lightgray'), (17, 'lightgrey'), (18, 'gainsboro'), (19, 'whitesmoke'),
                (20, 'white'), (21, 'snow'), (22, 'rosybrown'), (23, 'lightcoral'),
                (24, 'indianred'), (25, 'brown'), (26, 'firebrick'), (27, 'maroon'),
                (28, 'darkred'), (29, 'red'), (30, 'mistyrose'), (31, 'salmon'),
                (32, 'tomato'), (33, 'darksalmon'), (34, 'coral'), (35, 'orangered'),
                (36, 'lightsalmon'), (37, 'sienna'), (38, 'seashell'), (39, 'chocolate'),
                (40, 'saddlebrown'), (41, 'sandybrown'), (42, 'peachpuff'), (43, 'peru'),
                (44, 'linen'), (45, 'bisque'), (46, 'darkorange'), (47, 'burlywood'),
                (48, 'antiquewhite'), (49, 'tan'), (50, 'navajowhite'), (51, 'blanchedalmond'),
                (52, 'papayawhip'), (53, 'moccasin'), (54, 'orange'), (55, 'wheat'),
                (56, 'oldlace'), (57, 'floralwhite'), (58, 'darkgoldenrod'), (59, 'goldenrod'),
                (60, 'cornsilk'), (61, 'gold'), (62, 'lemonchiffon'), (63, 'khaki'),
                (64, 'palegoldenrod'), (65, 'darkkhaki'), (66, 'ivory'), (67, 'beige'),
                (68, 'lightyellow'), (69, 'lightgoldenrodyellow'), (70, 'olive'), (71, 'yellow'),
                (72, 'olivedrab'), (73, 'yellowgreen'), (74, 'darkolivegreen'), (75, 'greenyellow'),
                (76, 'chartreuse'), (77, 'lawngreen'), (78, 'honeydew'), (79, 'darkseagreen'),
                (80, 'palegreen'), (81, 'lightgreen'), (82, 'forestgreen'), (83, 'limegreen'),
                (84, 'darkgreen'), (85, 'green'), (86, 'lime'), (87, 'seagreen'),
                (88, 'mediumseagreen'), (89, 'springgreen'), (90, 'mintcream'), (91, 'mediumspringgreen'),
                (92, 'mediumaquamarine'), (93, 'aquamarine'), (94, 'turquoise'), (95, 'lightseagreen'),
                (96, 'mediumturquoise'), (97, 'azure'), (98, 'lightcyan'), (99, 'paleturquoise'),
                (100, 'darkslategray'), (101, 'darkslategrey'), (102, 'teal'), (103, 'darkcyan'),
                (104, 'aqua'), (105, 'cyan'), (106, 'darkturquoise'), (107, 'cadetblue'),
                (108, 'powderblue'), (109, 'lightblue'), (110, 'deepskyblue'), (111, 'skyblue'),
                (112, 'lightskyblue'), (113, 'steelblue'), (114, 'aliceblue'), (115, 'dodgerblue'),
                (116, 'lightslategray'), (117, 'lightslategrey'), (118, 'slategray'), (119, 'slategrey'),
                (120, 'lightsteelblue'), (121, 'cornflowerblue'), (122, 'royalblue'), (123, 'ghostwhite'),
                (124, 'lavender'), (125, 'midnightblue'), (126, 'navy'), (127, 'darkblue'),
                (128, 'mediumblue'), (129, 'blue'), (130, 'slateblue'), (131, 'darkslateblue'),
                (132, 'mediumslateblue'), (133, 'mediumpurple'), (134, 'rebeccapurple'), (135, 'blueviolet'),
                (136, 'indigo'), (137, 'darkorchid'), (138, 'darkviolet'), (139, 'mediumorchid'),
                (140, 'thistle'), (141, 'plum'), (142, 'violet'), (143, 'purple'),
                (144, 'darkmagenta'), (145, 'fuchsia'), (146, 'magenta'), (147, 'orchid'),
                (148, 'mediumvioletred'), (149, 'deeppink'), (150, 'hotpink'), (151, 'lavenderblush'),
                (152, 'palevioletred'), (153, 'crimson'), (154, 'pink'), (155, 'lightpink'))

StyleChoices = ((0, 'solid'), (1, 'loosely dotted'), (2, 'dotted'), (3, 'densely dotted'),
                (4, 'loosely dashed'), (5, 'dashed'), (6, 'densely dashed'),
                (7, 'loosely dashdotted'), (8, 'dashdotted'), (9, 'densely dashdotted'),
                (10, 'loosely dashdotdotted'), (11, 'dashdotdotted'), (12, 'densely dashdotdotted'))

LineStyles = [(0, ()), (0, (1, 10)), (0, (1, 5)), (0, (1, 1)),
              (0, (5, 10)), (0, (5, 5)), (0, (5, 1)),
              (0, (3, 10, 1, 10)), (0, (3, 5, 1, 5)), (0, (3, 1, 1, 1)),
              (0, (3, 10, 1, 10, 1, 10)), (0, (3, 5, 1, 5, 1, 5)), (0, (3, 1, 1, 1, 1, 1))]

MarkerChoices = ((0, 'point'), (1, 'pixel'), (2, 'circle'),
                 (3, 'triangle_down'), (4, 'triangle_up'), (5, 'triangle_left'), (6, 'triangle_right'),
                 (7, 'tri_down'), (8, 'tri_up'), (9, 'tri_left'), (10, 'tri_right'),
                 (11, 'octagon'), (12, 'square'), (13, 'pentagon'), (14, 'star'),
                 (15, 'hexagon1'), (16, 'hexagon2'), (17, 'plus'), (18, 'cross'),
                 (19, 'diamond'), (20, 'thin_diamond'), (21, 'vline'), (22, 'hline'))

Markers = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4',
           '8', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '-']

ColormapChoices = ((0, 'viridis'), (1, 'plasma'), (2, 'inferno'), (3, 'magma'), (4, 'cividis'),
                   (5, 'Greys'), (6, 'Purples'), (7, 'Blues'), (8, 'Greens'), (9, 'Oranges'),
                   (10, 'Reds'), (11, 'YlOrBr'), (12, 'YlOrRd'), (13, 'OrRd'), (14, 'PuRd'),
                   (15, 'RdPu'), (16, 'BuPu'), (17, 'GnBu'), (18, 'PuBu'), (19, 'YlGnBu'),
                   (20, 'PuBuGn'), (21, 'BuGn'), (22, 'YlGn'), (23, 'binary'), (24, 'gist_yarg'),
                   (25, 'gist_gray'), (26, 'gray'), (27, 'bone'), (28, 'pink'), (29, 'spring'),
                   (30, 'summer'), (31, 'autumn'), (32, 'winter'), (33, 'cool'), (34, 'Wistia'),
                   (35, 'hot'), (36, 'afmhot'), (37, 'gist_heat'), (38, 'copper'), (39, 'PiYG'),
                   (40, 'PRGn'), (41, 'BrBG'), (42, 'PuOr'), (43, 'RdGy'), (44, 'RdBu'),
                   (45, 'RdYlBu'), (46, 'RdYlGn'), (47, 'Spectral'), (48, 'coolwarm'), (49, 'bwr'),
                   (50, 'seismic'), (51, 'twilight'), (52, 'twilight_shifted'), (53, 'hsv'), (54, 'Pastel1'),
                   (55, 'Pastel2'), (56, 'Paired'), (57, 'Accent'), (58, 'Dark2'), (59, 'Set1'),
                   (60, 'Set2'), (61, 'Set3'), (62, 'tab10'), (63, 'tab20'), (64, 'tab20b'),
                   (65, 'tab20c'), (66, 'flag'), (67, 'prism'), (68, 'ocean'), (69, 'gist_earth'),
                   (70, 'terrain'), (71, 'gist_stern'), (72, 'gnuplot'), (73, 'gnuplot2'), (74, 'CMRmap'),
                   (75, 'cubehelix'), (76, 'brg'), (77, 'gist_rainbow'), (78, 'rainbow'), (79, 'jet'),
                   (80, 'turbo'), (81, 'nipy_spectral'), (82, 'gist_ncar'))

class Item(Updated, Remote):
    upper = models.ForeignKey(Area, verbose_name='Plot area', on_delete=models.CASCADE)
    url = models.CharField(verbose_name='URL', max_length=256)
    columnx =  models.CharField(verbose_name='Column X', max_length=100)
    columny =  models.CharField(verbose_name='Column Y', max_length=100, blank=True)
    TypeChoices = ((0, 'Line'), (1, 'LineMarker'), (2, 'Scatter'), (3, 'Bar'), (4, 'Histgram'))
    type = models.PositiveSmallIntegerField(verbose_name='Type', choices=TypeChoices, default=0)
    color = models.PositiveSmallIntegerField(verbose_name='Color', choices=ColorChoices, default=0)
    edgecolor = models.PositiveSmallIntegerField(verbose_name='Edge color', choices=ColorChoices, default=0)
    linewidth = models.FloatField(verbose_name='Line width', default=1.0)
    linestyle = models.PositiveSmallIntegerField(verbose_name='Line style', choices=StyleChoices, default=0)
    marker = models.PositiveSmallIntegerField(verbose_name='Marker', choices=MarkerChoices, default=0)
    markersize = models.PositiveSmallIntegerField(verbose_name='Marker size', default=20)
    bins = models.PositiveSmallIntegerField(verbose_name='Bins', default=10)
    columnc = models.CharField(verbose_name='Column Color', max_length=100, blank=True)
    colormap = models.PositiveSmallIntegerField(verbose_name='Colormap', choices=ColormapChoices, default=0)
    label = models.CharField(verbose_name='Label', max_length=100, blank=True)
    order = models.SmallIntegerField(verbose_name='Order')

    def title(self):
        return '%s : %s_%d' % (self.upper.title(), self.name(), self.order)

    def name(self):
        return self.__class__.__name__

    def get_detail_url(self):
        return reverse('plot:area_update', kwargs={'pk': self.upper.id})

    def get_update_url(self):
        return reverse('plot:item_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('plot:item_delete', kwargs={'pk': self.id})

    def get_xy(self, **kwargs):
        if self.url.startswith('http'):
            if self.url.startswith(kwargs['request_host'] ):
                response = requests.get(self.url, cookies=kwargs['request_cookies'])
            else:
                response = requests.get(self.url)
        else:
            response = requests.get(kwargs['request_host'] + self.url,
                                    cookies=kwargs['request_cookies'])
        if response.status_code != 200:
            return [0, 0], [0, 0], None
        else:
            buf = BytesIO(response.content)
            df = pd.read_csv(buf)
            buf.close()
        if self.columnx in df.columns.values:
            x = df[self.columnx]
        else:
            x = df.index.values
        if self.columny in df.columns.values:
            y = df[self.columny]
        else:
            y = df.index.values
        if self.columnc in df.columns.values:
            c = df[self.columnc]
        else:
            c = None
        return x, y, c

    def plot(self, **kwargs):
        if self.type == 0:
            x, y, c = self.get_xy(**kwargs)
            plt.plot(x, y, linewidth=self.linewidth, linestyle=LineStyles[self.linestyle],
                     color=self.get_color_display(), label=self.label)
        elif self.type == 1:
            x, y, c = self.get_xy(**kwargs)
            plt.plot(x, y, linewidth=self.linewidth, linestyle=LineStyles[self.linestyle],
                     color=self.get_color_display(), marker=Markers[self.marker], label=self.label)
        elif self.type == 2:
            x, y, c = self.get_xy(**kwargs)
            if c is None:
                plt.scatter(x, y, color=self.get_color_display(), edgecolors=self.get_edgecolor_display(),
                            marker=Markers[self.marker], s=self.markersize, label=self.label)
            else:
                cmap = matplotlib.colormaps[self.get_colormap_display()]
                plt.scatter(x, y, marker=Markers[self.marker], s=self.markersize, label=self.label,
                            c=c, cmap=cmap)
        elif self.type == 3:
            x, y, c = self.get_xy(**kwargs)
            plt.bar(x, y, color=self.get_color_display(), edgecolor=self.get_edgecolor_display(),
                    linewidth=self.linewidth, align='center', label=self.label)
        elif self.type == 4:
            x, y, c = self.get_xy(**kwargs)
            plt.hist(x, color=self.get_color_display(), edgecolor=self.get_edgecolor_display(),
                     bins=self.bins)

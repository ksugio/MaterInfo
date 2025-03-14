from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, ModelUploadTo, Unique
from plot.models.item import ColormapChoices
from .filter import Filter
from .regression_lib import HParam2Dict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA, KernelPCA, SparsePCA
from sklearn.manifold import SpectralEmbedding, Isomap, LocallyLinearEmbedding, TSNE
from umap import UMAP
from io import BytesIO
import pandas as pd
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#def PCAUploadTo(instance, filename):
#    return filename

def ReductionModel(dparam, scaler, method):
    pipeline = []
    if scaler == 1:
        pipeline.append(('minmax', MinMaxScaler()))
    elif scaler == 2:
        pipeline.append(('standard', StandardScaler()))
    if method == 0:
        pipeline.append(('pca', PCA(**dparam)))
    elif method == 1:
        pipeline.append(('kernalpca', KernelPCA(**dparam)))
    elif method == 2:
        pipeline.append(('sparsepca', SparsePCA(**dparam)))
    elif method == 3:
        pipeline.append(('specembed', SpectralEmbedding(**dparam)))
    elif method == 4:
        pipeline.append(('isomap', Isomap(**dparam)))
    elif method == 5:
        pipeline.append(('lle', LocallyLinearEmbedding(**dparam)))
    elif method == 6:
        pipeline.append(('tsne', TSNE(**dparam)))
    elif method == 7:
        pipeline.append(('umap', UMAP(**dparam)))
    return Pipeline(pipeline)

class Reduction(Created, Updated, Remote, Unique):
    upper = models.ForeignKey(Filter, verbose_name='Filter', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    ScalerChoices = ((0, 'None'), (1, 'MinMax'), (2, 'Standard'))
    scaler = models.PositiveSmallIntegerField(verbose_name='Scaler', choices=ScalerChoices, default=2)
    MethodChoices = ((0, 'PCA'), (1, 'KernelPCA'), (2, 'SparsePCA'), (3, 'SpectralEmbedding'), (4, 'Isomap'),
                     (5, 'LocallyLinearEmbedding'), (6, 't-SNE'), (7, 'UMAP'))
    method = models.PositiveSmallIntegerField(verbose_name='Method', choices=MethodChoices, default=0)
    hparam = models.TextField(verbose_name='Hyperparameter', blank=True)
    drop = models.CharField(verbose_name='Drop columns', max_length=250, blank=True)
    label = models.CharField(verbose_name='Label', max_length=50, blank=True, null=True)
    colormap = models.PositiveSmallIntegerField(verbose_name='Colormap', choices=ColormapChoices, default=0)
    colorbar = models.BooleanField(verbose_name='Colorbar', default=False)
    nplot = models.PositiveSmallIntegerField(verbose_name='Number of plot features', default=10)
    file = models.FileField(verbose_name='File', upload_to=ModelUploadTo, blank=True, null=True)
    results = models.TextField(verbose_name='JSON Results', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('collect:reduction_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('collect:reduction_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('collect:reduction_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('collect:reduction_delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('collect:api_reduction_update', kwargs={'pk': self.id})

    def recent_updated_at(self):
        updated_at = self.upper.recent_updated_at()
        if self.updated_at > updated_at:
            updated_at = self.updated_at
        return updated_at

    def drop_columns(self, df):
        ldrop = self.drop.replace('\n', '').replace('\r', '').replace(' ', '').split(',')
        cols = []
        for col in ldrop:
            if col in df.columns:
                cols.append(col)
        return df.drop(columns=cols)

    def fit_transform(self):
        df = self.upper.check_read_csv()
        if df is None:
            return
        if df.isnull().values.sum() > 0:
            return
        if self.label in df.columns:
            label = df.pop(self.label)
        else:
            label = None
        features = self.upper.upper.drophead(df)
        features = self.drop_columns(features)
        dparam = HParam2Dict(self.hparam)
        model = ReductionModel(dparam, self.scaler, self.method)
        dr_features = model.fit_transform(features)
        if self.method == 0:
            results = {
                'Ratio': model['pca'].explained_variance_ratio_.tolist(),
                'Components': model['pca'].components_.tolist(),
                'Columns': features.columns.tolist()
            }
        else:
            results = {}
        self.results = json.dumps(results)
        columns = ['PC%d' % (i + 1) for i in range(dr_features.shape[1])]
        drdf = pd.DataFrame(dr_features, columns=columns)
        if label is not None:
            drdf['Label'] = label
        self.save_csv(drdf)

    def save_csv(self, df):
        buf = BytesIO()
        df.to_csv(buf, index=False, mode="wb", encoding='UTF-8')
        self.file.save('Reduction.csv', buf, save=False)
        buf.close()

    def read_csv(self):
        if self.file:
            with self.file.open('r') as f:
                return pd.read_csv(f)
        return None

    def plot_scatter(self, **kwargs):
        drdf = self.read_csv()
        fig, ax = plt.subplots()
        if 'Label' in drdf.columns:
            cmap = matplotlib.colormaps[self.get_colormap_display()]
            sc = ax.scatter(drdf['PC1'], drdf['PC2'], marker='.', c=list(drdf['Label']), cmap=cmap)
            if self.colorbar:
                fig.colorbar(sc)
        else:
            ax.scatter(drdf['PC1'], drdf['PC2'], marker='.')
        ax.set_xlabel('PC1')
        ax.set_ylabel('PC2')
        return fig

    def plot_components(self, **kwargs):
        results = json.loads(self.results)
        if 'Ratio' not in results:
            return
        fig, ax = plt.subplots(1, 3, figsize=(18, 4.5))
        # plot 1
        ratio = results['Ratio']
        ran = np.arange(1, len(ratio) + 1)
        ax[0].bar(ran, ratio, color='white', edgecolor='black')
        ax[0].step(ran, np.cumsum(ratio))
        ax[0].set_xlabel('Principal Components')
        ax[0].set_ylabel('Explained Variance Ratio')
        # plot 2
        cols, comps = self.sortcomps(results['Columns'], results['Components'][0])
        ax[1].bar(cols, comps, color='white', edgecolor='black')
        ax[1].set_xlabel('Components of PC1')
        ax[1].set_ylabel('Eigenvector')
        ax[1].xaxis.set_tick_params(rotation=90)
        # plot 3
        cols, comps = self.sortcomps(results['Columns'], results['Components'][1])
        ax[2].bar(cols, comps, color='white', edgecolor='black')
        ax[2].set_xlabel('Components of PC2')
        ax[2].set_ylabel('Eigenvector')
        ax[2].xaxis.set_tick_params(rotation=90)
        return fig

    def sortcomps(self, columns, components):
        data = list(zip(columns, components))
        data = sorted(data, key=lambda x: abs(x[1]), reverse=True)[:self.nplot]
        return zip(*data)

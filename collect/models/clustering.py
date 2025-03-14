from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, Task, ModelUploadTo, Unique
from plot.models.item import ColormapChoices
from .filter import Filter
from sklearn.metrics import silhouette_samples, silhouette_score
from io import BytesIO
import numpy as np
import pandas as pd
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class Clustering(Created, Updated, Remote, Task, Unique):
    upper = models.ForeignKey(Filter, verbose_name='Filter', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    ScalerChoices = ((0, 'None'), (1, 'MinMax'), (2, 'Standard'))
    scaler = models.PositiveSmallIntegerField(verbose_name='Scaler', choices=ScalerChoices, default=0)
    ReductionChoices = ((0, 'PCA'), (1, 'Isomap'), (2, 't-SNE'), (3, 'UMAP'))
    reduction = models.PositiveSmallIntegerField(verbose_name='Reduction', choices=ReductionChoices, default=0)
    n_components = models.PositiveSmallIntegerField(verbose_name='Number of PCA components', default=8)
    MethodChoices = ((0, 'K-Means'), (1, 'Mean-shift'), (2, 'SpectralClustering'), (3, 'AgglomerativeClustering'),
                     (4, 'DBSCAN'), (5, 'GaussianMixtures'))
    method = models.PositiveSmallIntegerField(verbose_name='Method', choices=MethodChoices, default=0)
    hparam = models.TextField(verbose_name='Hyperparameter', blank=True)
    drop = models.CharField(verbose_name='Drop columns', max_length=250, blank=True)
    colormap = models.PositiveSmallIntegerField(verbose_name='Colormap', choices=ColormapChoices, default=0)
    ntrials = models.PositiveIntegerField(verbose_name='Number of trials', default=20)
    ScoreChoices = ((0, 'Silhouette'), (1, 'Davies-Bouldin'), (2, 'Calinski-Harabasz'))
    score = models.PositiveSmallIntegerField(verbose_name='Score', choices=ScoreChoices, default=0)
    file = models.FileField(verbose_name='File', upload_to=ModelUploadTo, blank=True, null=True)
    results = models.TextField(verbose_name='JSON Results', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('collect:clustering_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('collect:clustering_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('collect:clustering_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('collect:clustering_delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('collect:api_clustering_update', kwargs={'pk': self.id})

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

    def dataset(self):
        df = self.upper.check_read_csv()
        if df is None:
            return
        if df.isnull().values.sum() > 0:
            return
        features = self.upper.upper.drophead(df)
        features = self.drop_columns(features)
        return features

    def save_csv(self, df):
        buf = BytesIO()
        df.to_csv(buf, index=False, mode="wb", encoding='UTF-8')
        self.file.save('Clustering.csv', buf, save=False)
        buf.close()

    def read_csv(self):
        if self.file:
            with self.file.open('r') as f:
                return pd.read_csv(f)
        return None

    def plot(self, **kwargs):
        df = self.read_csv()
        if df is None:
            return
        label = df.pop('Label')
        results = json.loads(self.results)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
        # Scatter
        cmap = matplotlib.colormaps[self.get_colormap_display()]
        ax1.scatter(df['PC1'], df['PC2'], marker='.', c=list(label), cmap=cmap)
        if 'cluster_centers' in results:
            centers = np.array(results['cluster_centers'])
            ax1.scatter(centers[:, 0], centers[:, 1], marker='o', c='white', s=200, edgecolor='k')
            for i, c in enumerate(centers):
                ax1.scatter(c[0], c[1], marker="$%d$" % i, s=50, edgecolor="k")
        ax1.set_xlabel('PC1')
        ax1.set_ylabel('PC2')
        # Silhouette
        labels = list(set(label))
        if len(labels) < 2:
            return fig
        minl = min(labels)
        maxl = max(labels)
        silhouette_avg = silhouette_score(df, label)
        silhouette = silhouette_samples(df, label)
        y_lower = 10
        y_title = []
        y_value = []
        for i in labels:
            ith = silhouette[label == i]
            ith.sort()
            size_i = ith.shape[0]
            y_upper = y_lower + size_i
            color = cmap((i - minl) / (maxl - minl))
            ax2.fill_betweenx(np.arange(y_lower, y_upper), 0, ith,
                             facecolor=color, edgecolor=color, alpha=0.7)
            y_title.append(i)
            y_value.append(y_lower + 0.5 * size_i)
            y_lower = y_upper + 10
        ax2.axvline(x=silhouette_avg, color="red", linestyle="--")
        ax2.set_xlabel("The silhouette coefficient values")
        ax2.set_ylabel("Cluster label")
        ax2.set_yticks(y_value, y_title)
        return fig

    def plot_trials(self, **kwargs):
        results = json.loads(self.results)
        if 'trials' in results:
            trials = results['trials']
            name = kwargs['name']
            if trials and name in trials['best_param']:
                fig, ax = plt.subplots()
                param = [d[name] for d in trials['params']]
                ax.plot(param, trials['values'], 'o')
                ax.plot(trials['best_param'][name], trials['best_value'], 'o')
                ax.set_xlabel(name)
                if self.score == 0:
                    ax.set_ylabel('Silhouette Score')
                elif self.score == 1:
                    ax.set_ylabel('Davies-Bouldin Score')
                elif self.score == 2:
                    ax.set_ylabel('Calinski-Harabasz Score')
                return fig

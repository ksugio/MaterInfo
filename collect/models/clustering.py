import pandas as pd
from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, ModelUploadTo
from .filter import Filter
from .regression_lib import HParam2Dict, Dict2HParam
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import Isomap, TSNE
from umap import UMAP
from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth, SpectralClustering, AgglomerativeClustering, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_samples, silhouette_score, davies_bouldin_score, calinski_harabasz_score
from io import BytesIO
import numpy as np
import pandas as pd
import json
import optuna
import warnings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def ClusteringModel(dparam, method):
    if method == 0:
        warnings.simplefilter('ignore', FutureWarning)
        return KMeans(**dparam)
    elif method == 1:
        return MeanShift(**dparam)
    elif method == 2:
        return SpectralClustering(**dparam)
    elif method == 3:
        return AgglomerativeClustering(**dparam)
    elif method == 4:
        return DBSCAN(**dparam)
    elif method == 5:
        return GaussianMixture(**dparam)

def ClusteringCoef(model, method):
    if method == 0:
        return {
            'cluster_centers': model.cluster_centers_.tolist(),
            'interia': model.inertia_
        }
    elif method == 1:
        centers = model.cluster_centers_.tolist()
        return {
            'cluster_centers': centers
        }
    elif method == 2:
        return {}
    elif method == 3:
        return {}
    elif method == 4:
        return {}
    elif method == 5:
        return {}

class ClusteringObjective:
    def __init__(self, X, dparam, method, score):
        self.X = X
        self.dparam = dparam
        self.method = method
        self.score = score
        self.bandwidth = estimate_bandwidth(self.X)

    def __call__(self, trial):
        param = self.dparam
        if self.method == 0: # KMeans
            param['n_clusters'] = trial.suggest_int('n_clusters', 2, 50)
        elif self.method == 1: # MeanShift
            param['bandwidth'] = trial.suggest_float('bandwidth', 0.01, 3*self.bandwidth)
        elif self.method == 2:  # SpectralClustering
            param['n_clusters'] = trial.suggest_int('n_clusters', 2, 50)
        elif self.method == 3: # AgglomerativeClustering
            param['n_clusters'] = trial.suggest_int('n_clusters', 2, 50)
        elif self.method == 4: # DBSCAN
            param['eps'] = trial.suggest_float('eps', 0.01, 3 * self.bandwidth)
        elif self.method == 5: # GaussianMixture
            param['n_components'] = trial.suggest_int('n_components', 2, 50)
        model = ClusteringModel(param, self.method)
        pred = model.fit_predict(self.X)
        if self.score == 0:
            if len(set(pred)) > 1:
                return silhouette_score(self.X, pred)
            else:
                return -1.0
        elif self.score == 1:
            if len(set(pred)) > 1:
                return davies_bouldin_score(self.X, pred)
            else:
                return 1.0e10
        elif self.score == 2:
            if len(set(pred)) > 1:
                return calinski_harabasz_score(self.X, pred)
            else:
                return -1.0e10

class Clustering(Created, Updated, Remote):
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
    ColormapChoices = ((0, 'viridis'), (1, 'gray'), (2, 'rainbow'), (3, 'jet'))
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

    def recent_updated_at(self):
        updated_at = self.upper.recent_updated_at()
        if self.updated_at > updated_at:
            updated_at = self.updated_at
        return updated_at

    def optimize(self, features, dparam):
        if self.score == 0:
            direction = 'maximize'
        elif self.score == 1:
            direction = 'minimize'
        elif self.score == 2:
            direction = 'maximize'
        study = optuna.create_study(direction=direction)
        objective = ClusteringObjective(features, dparam, self.method, self.score)
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        study.optimize(objective, n_trials=self.ntrials)
        dparam.update(study.best_params)
        self.hparam = Dict2HParam(dparam)
        ids = [t._trial_id for t in study.get_trials()]
        values = [t.values[0] for t in study.get_trials()]
        params = [t.params for t in study.get_trials()]
        trials = {
            'ids': ids,
            'values': values,
            'params': params,
            'best_id': study.best_trial._trial_id,
            'best_value': study.best_trial.values[0],
            'best_param': study.best_trial.params
        }
        return dparam, trials

    def drop_columns(self, df):
        ldrop = self.drop.replace('\n', '').replace('\r', '').replace(' ', '').split(',')
        cols = []
        for col in ldrop:
            if col in df.columns:
                cols.append(col)
        return df.drop(columns=cols)

    def train(self, optimize):
        df = self.upper.check_read_csv()
        if df is None:
            return
        if df.isnull().values.sum() > 0:
            return
        features = self.upper.upper.drophead(df)
        features = self.drop_columns(features)
        pipeline = []
        if self.scaler == 1:
            pipeline.append(('minmax', MinMaxScaler()))
        elif self.scaler == 2:
            pipeline.append(('standard', StandardScaler()))
        if self.n_components < len(features.columns):
            param = { 'n_components': self.n_components }
        else:
            param = {}
        if self.reduction == 0:
            pipeline.append(('pca', PCA(**param)))
        elif self.reduction == 1:
            pipeline.append(('isomap', Isomap(**param)))
        elif self.reduction == 2:
            param['n_components'] = 3
            pipeline.append(('tsne', TSNE(**param)))
        elif self.reduction == 3:
            pipeline.append(('umap', UMAP(**param)))
        model = Pipeline(pipeline)
        pca_features = model.fit_transform(features)
        dparam = HParam2Dict(self.hparam)
        if optimize:
            dparam, trials = self.optimize(pca_features, dparam)
        else:
            trials = {}
        model2 = ClusteringModel(dparam, self.method)
        pred = model2.fit_predict(pca_features)
        columns = ['PC%d' % (i + 1) for i in range(pca_features.shape[1])]
        df = pd.DataFrame(pca_features, columns=columns)
        df['Label'] = pred
        coef = ClusteringCoef(model2, self.method)
        if len(set(pred)) > 1:
            if self.score == 0:
                score = silhouette_score(pca_features, pred)
            elif self.score == 1:
                score = davies_bouldin_score(pca_features, pred)
            elif self.score == 2:
                score = calinski_harabasz_score(pca_features, pred)
        else:
            score = None
        results = {
            'score': float(score),
            'trials': trials,
            **coef
        }
        self.results = json.dumps(results)
        self.save_csv(df)

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
        label = df.pop('Label')
        results = json.loads(self.results)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
        # Scatter
        cmap = plt.cm.get_cmap(self.get_colormap_display())
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

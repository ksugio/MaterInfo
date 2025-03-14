from .regression_lib import HParam2Dict, Dict2HParam
from .clustering import Clustering
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import Isomap, TSNE
from umap import UMAP
from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth, SpectralClustering, AgglomerativeClustering, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
import numpy as np
import pandas as pd
import optuna
import warnings
import json

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

def Optimize(features, score, dparam, method, ntrials):
    if score == 0:
        direction = 'maximize'
    elif score == 1:
        direction = 'minimize'
    elif score == 2:
        direction = 'maximize'
    study = optuna.create_study(direction=direction)
    objective = ClusteringObjective(features, dparam, method, score)
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study.optimize(objective, n_trials=ntrials)
    dparam.update(study.best_params)
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

def ClusteringExec(features, hparam, optimize, scaler, n_components, reduction,
                   method, score, ntrials, task_id):
    features = np.array(features)
    pipeline = []
    if scaler == 1:
        pipeline.append(('minmax', MinMaxScaler()))
    elif scaler == 2:
        pipeline.append(('standard', StandardScaler()))
    if n_components < len(features[0]):
        param = { 'n_components': n_components }
    else:
        param = {}
    if reduction == 0:
        pipeline.append(('pca', PCA(**param)))
    elif reduction == 1:
        pipeline.append(('isomap', Isomap(**param)))
    elif reduction == 2:
        param['n_components'] = 3
        pipeline.append(('tsne', TSNE(**param)))
    elif reduction == 3:
        pipeline.append(('umap', UMAP(**param)))
    model = Pipeline(pipeline)
    pca_features = model.fit_transform(features)
    dparam = HParam2Dict(hparam)
    if optimize:
        dparam, trials = Optimize(pca_features, score, dparam, method, ntrials)
        hparam = Dict2HParam(dparam)
    else:
        trials = {}
    model2 = ClusteringModel(dparam, method)
    pred = model2.fit_predict(pca_features)
    pca_label = {}
    for i in range(pca_features.shape[1]):
        pca_label['PC%d' % (i + 1)] = pca_features[:, i].tolist()
    pca_label['Label'] = pred.tolist()
    coef = ClusteringCoef(model2, method)
    if len(set(pred)) > 1:
        if score == 0:
            scored = silhouette_score(pca_features, pred)
        elif score == 1:
            scored = davies_bouldin_score(pca_features, pred)
        elif score == 2:
            scored = calinski_harabasz_score(pca_features, pred)
    else:
        scored = None
    results = {
        'score': float(scored),
        'trials': trials,
        **coef
    }
    model = Clustering.objects.get(task_id=task_id)
    model.hparam = hparam
    pdf = pd.DataFrame(pca_label)
    model.save_csv(pdf)
    model.results = json.dumps(results)
    model.save()


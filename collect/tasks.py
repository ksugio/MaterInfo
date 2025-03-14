from celery import shared_task, current_task
from .models.regression_lib import RegressionExec, RegreSHAPExec
from .models.inverse_lib import InverseExec
from .models.classification_lib import ClassificationExec, ClassSHAPExec
from .models.clustering_lib import ClusteringExec

@shared_task(name='regression-task', queue='collect')
def RegressionTask(features, obj, hparam, optimize, testsize, randomts, scaler,
                   pca, n_components, method, nsplits, random, ntrials, columns, **kwargs):
    return RegressionExec(features, obj, hparam, optimize, testsize, randomts, scaler,
                          pca, n_components, method, nsplits, random, ntrials, columns,
                          current_task.request.id)

@shared_task(name='regreshap-task', queue='collect')
def RegreSHAPTask(model_data, features, obj, columns, use_kernel, kmeans, nsample,  **kwargs):
    return RegreSHAPExec(model_data, features, obj, columns, use_kernel, kmeans, nsample,
                         current_task.request.id)

@shared_task(name='inverse-task', queue='collect')
def InverseTask(regdata, suggests, seed, ntrials, **kwargs):
    return InverseExec(regdata, suggests, seed, ntrials, current_task.request.id)

@shared_task(name='classification-task', queue='collect')
def ClassificationTask(features, obj, hparam, optimize, testsize, randomts, scaler,
                       pca, n_components, method, nsplits, random, ntrials, columns, **kwargs):
    return ClassificationExec(features, obj, hparam, optimize, testsize, randomts, scaler,
                              pca, n_components, method, nsplits, random, ntrials, columns,
                              current_task.request.id)

@shared_task(name='classshap-task', queue='collect')
def ClassSHAPTask(model_data, features, obj, columns, use_kernel, kmeans, nsample, **kwargs):
    return ClassSHAPExec(model_data, features, obj, columns, use_kernel, kmeans, nsample,
                         current_task.request.id)

@shared_task(name='clustering-task', queue='collect')
def ClusteringTask(features, hparam, optimize, scaler, n_components, reduction,
                   method, score, ntrials, **kwargs):
    return ClusteringExec(features, hparam, optimize, scaler, n_components, reduction,
                          method, score, ntrials, current_task.request.id)

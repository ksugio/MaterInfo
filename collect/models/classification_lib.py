from .classification import Classification
from .classshap import ClassSHAP
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import f1_score, accuracy_score, classification_report
from sklearn.linear_model import RidgeClassifier, LogisticRegression
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import LinearSVC, SVC
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from .regression_lib import HParam2Dict, Dict2HParam
from io import BytesIO
import numpy as np
import optuna
import shap
import joblib
import json

def ClassificationModel(dparam, scaler, pca, n_components, method):
    pipeline = []
    if scaler == 1:
        pipeline.append(('minmax', MinMaxScaler()))
    elif scaler == 2:
        pipeline.append(('standard', StandardScaler()))
    if pca:
        pipeline.append(('pca', PCA(n_components=n_components)))
    if method == 0:
        pipeline.append(('ridge', RidgeClassifier(**dparam)))
    elif method == 1:
        pipeline.append(('logistic', LogisticRegression(max_iter=1000, **dparam)))
    elif method == 2:
        pipeline.append(('gpc', GaussianProcessClassifier(**dparam)))
    elif method == 3:
        pipeline.append(('gnb', GaussianNB(**dparam)))
    elif method == 4:
        pipeline.append(('knc', KNeighborsClassifier(**dparam)))
    elif method == 5:
        pipeline.append(('rfc', RandomForestClassifier(**dparam)))
    elif method == 6:
        pipeline.append(('gbc', GradientBoostingClassifier(**dparam)))
    elif method == 7:
        pipeline.append(('lsvc', LinearSVC(**dparam)))
    elif method == 8:
        pipeline.append(('svc', SVC(**dparam)))
    elif method == 9:
        pipeline.append(('mlpc', MLPClassifier(max_iter=1000, **dparam)))
    elif method == 10:
        pipeline.append(('xgb', XGBClassifier(**dparam)))
    elif method == 11:
        pipeline.append(('lgbm', LGBMClassifier(importance_type='gain', verbose=-1, **dparam)))
    return Pipeline(pipeline)

def ClassificationCoef(model, method):
    if method == 0:
        return {}
    elif method == 1:
        return {}
    elif method == 2:
        return {}
    elif method == 3:
        return {}
    elif method == 4:
        return {}
    elif method == 5:
        return {'importances': model['rfc'].feature_importances_.tolist()}
    elif method == 6:
        return {'importances': model['gbc'].feature_importances_.tolist()}
    elif method == 7:
        return {}
    elif method == 8:
        return {}
    elif method == 9:
        return {}
    elif method == 10:
        score = model['xgb'].get_booster().get_score(importance_type="gain")
        importances = list(score.values())
        return {'importances': importances}
    elif method == 11:
        return {'importances': model['lgbm'].feature_importances_.tolist()}

class ClassificationObjective:
    def __init__(self, X, Y, dparam, scaler, pca, n_components, method, nsplits, random):
        self.X = X
        self.Y = Y
        self.dparam = dparam
        self.scaler = scaler
        self.pca = pca
        self.n_components = n_components
        self.method = method
        self.nsplits = nsplits
        self.random = random

    def __call__(self, trial):
        param = self.dparam
        if self.method == 0: # Ridge
            param['alpha'] = trial.suggest_float('alpha', 0.01, 5, log=True)
        elif self.method == 1: # Logistic
            param['C'] = trial.suggest_float('C', 0.01, 5, log=True)
        elif self.method == 2: # GaussianProcess
            pass
        elif self.method == 3: # GaussianNB
            pass
        elif self.method == 4: # KNeighbors
            param['n_neighbors'] = trial.suggest_int('n_neighbors', 1, len(self.Y) / 2)
        elif self.method == 5: # RandomForest
            param['n_estimators'] = trial.suggest_int('n_estimators', 10, 200)
        elif self.method == 6: # GradientBoosting
            param['n_estimators'] = trial.suggest_int('n_estimators', 10, 200)
            param['learning_rate'] = trial.suggest_float('learning_rate', 0.01, 5)
        elif self.method == 7: # LinearSVC
            param['C'] = trial.suggest_float('C', 1e-5, 1e5, log=True)
        elif self.method == 8: # SVC
            param['C'] = trial.suggest_float('C', 1e-5, 1e5, log=True)
        elif self.method == 9:  # MLPC
            param['alpha'] = trial.suggest_float('alpha', 0.0001, 0.01, log=True)
        elif self.method == 10:  # XGBoost
            param['eta'] = trial.suggest_float('eta', 0.0, 1.0)
        elif self.method == 11:  # LightGBM
            param['learning_rate'] = trial.suggest_float('learning_rate', 0.0, 1.0)
        model = ClassificationModel(param, self.scaler, self.pca, self.n_components, self.method)
        if self.random:
            kf = StratifiedKFold(n_splits=self.nsplits, shuffle=True, random_state=self.random)
        else:
            kf = StratifiedKFold(n_splits=self.nsplits)
        scores = []
        for train, test in kf.split(self.X, self.Y):
            xtrain, ytrain = self.X[train], self.Y[train]
            xtest, ytest = self.X[test], self.Y[test]
            model.fit(xtrain, ytrain)
            ypred = model.predict(self.X[test])
            scores.append(f1_score(ytest, ypred, average='macro'))
        if trial.should_prune():
            raise optuna.structs.TrialPruned()
        return np.mean(scores)

def Optimize(features, obj, dparam, scaler, pca, n_components, method, nsplits, random, ntrials):
    study = optuna.create_study(direction='maximize')
    objective = ClassificationObjective(features, obj, dparam, scaler, pca,
                                        n_components, method, nsplits, random)
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

def ClassificationExec(features, obj, hparam, optimize, testsize, randomts, scaler,
                       pca, n_components, method, nsplits, random, ntrials, columns, task_id):
    features = np.array(features)
    obj = np.array(obj)
    if testsize > 0.0 and testsize <= 0.5:
        if randomts:
            features, test_features, obj, test_obj = train_test_split(features, obj, test_size=testsize, stratify=obj, random_state=randomts)
        else:
            features, test_features, obj, test_obj = train_test_split(features, obj, test_size=testsize, stratify=obj)
    else:
        test_features = None
        test_obj = None
    dparam = HParam2Dict(hparam)
    if optimize:
        dparam, trials = Optimize(features, obj, dparam, scaler, pca, n_components,
                                  method, nsplits, random, ntrials)
        hparam = Dict2HParam(dparam)
    else:
        trials = {}
    # test with KFold
    model = ClassificationModel(dparam, scaler, pca, n_components, method)
    if random:
        kf = StratifiedKFold(n_splits=nsplits, shuffle=True, random_state=random)
    else:
        kf = StratifiedKFold(n_splits=nsplits)
    reports = []
    for i, (train, test) in enumerate(kf.split(features, obj)):
        xtrain, ytrain = features[train], obj[train]
        xtest, ytest = features[test], obj[test]
        model.fit(xtrain, ytrain)
        pred = model.predict(features)
        report = classification_report(ytest, pred[test], output_dict=True)
        report['id'] = i
        report['train_accuracy'] = accuracy_score(ytrain, pred[train])
        reports.append(report)
    accuracies = []
    train_accuracies = []
    for report in reports:
        accuracies.append(report['accuracy'])
        train_accuracies.append(report['train_accuracy'])
    mean_accuracy = np.mean(accuracies)
    mean_train_accuracy = np.mean(train_accuracies)
    # train
    model.fit(features, obj)
    pred = model.predict(features)
    all_train_accuracy = accuracy_score(obj, pred)
    if test_features is not None:
        test_pred = model.predict(test_features)
        all_report = classification_report(test_obj, test_pred, output_dict=True)
    coef = ClassificationCoef(model, method)
    if pca:
        columns = ['PC{}'.format(i) for i in range(1, n_components + 1)]
    results = {
        'reports': reports,
        'mean_accuracy': mean_accuracy,
        'mean_train_accuracy': mean_train_accuracy,
        'all_train_accuracy': all_train_accuracy,
        'columns': columns,
        'trials': trials,
        **coef
    }
    if test_features is not None:
        results['all_report'] = all_report
    cls = Classification.objects.get(task_id=task_id)
    cls.hparam = hparam
    cls.save_model(model)
    cls.results = json.dumps(results)
    cls.save()

def ClassSHAPExec(model_data, features, obj, columns, use_kernel, kmeans, nsample, task_id):
    buf = BytesIO(model_data)
    buf.write(model_data)
    model = joblib.load(buf)
    buf.close()
    targets = list(set(obj))
    features = np.array(features)
    step = 0
    if model.steps[step][0] == 'minmax' or model.steps[step][0] == 'standard':
        features = model[step].transform(features)
        step += 1
    if model.steps[step][0] == 'pca':
        features = model[step].transform(features)
        step += 1
    obj = np.array(obj)
    method = model.steps[step][0]
    if use_kernel and method != 'ridge':
        summary = shap.kmeans(features, kmeans)
        if method == 'lsvc' or method == 'svc':
            explainer = shap.KernelExplainer(model[step].predict, summary)
        else:
            explainer = shap.KernelExplainer(model[step].predict_proba, summary)
        if nsample < obj.shape[0]:
            x_test = features[:nsample]
        else:
            x_test = features
    elif method == 'ridge' or method == 'logistic':
        explainer = shap.LinearExplainer(model[step], features)
        x_test = features
    elif method == 'rfc' or method == 'xgb' or method == 'lgbm':
        explainer = shap.TreeExplainer(model[step])
        x_test = features
    elif method == 'lsvc' or method == 'svc':
        summary = shap.kmeans(features, kmeans)
        explainer = shap.KernelExplainer(model[step].predict, summary)
        if nsample < obj.shape[0]:
            x_test = features[:nsample]
        else:
            x_test = features
    else:
        summary = shap.kmeans(features, kmeans)
        explainer = shap.KernelExplainer(model[step].predict_proba, summary)
        if nsample < obj.shape[0]:
            x_test = features[:nsample]
        else:
            x_test = features
    shap_values = explainer.shap_values(X=x_test)
    shap_values = np.array(shap_values)
    results = {
        'shap_values': shap_values.tolist(),
        'x_test': x_test.tolist(),
        'columns': columns,
        'targets': targets
    }
    model = ClassSHAP.objects.get(task_id=task_id)
    model.results = json.dumps(results)
    model.save()

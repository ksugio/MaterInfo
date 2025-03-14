from .regression import Regression
from .regreshap import RegreSHAP
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import KFold, train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from io import BytesIO
import numpy as np
import pandas as pd
import optuna
import shap
import joblib
import json

def GetValueList(item):
    vl = []
    for vs in item[1:-1].split('$'):
        if vs:
            if vs.isdecimal():
                vl.append(int(vs))
            else:
                vl.append(float(vs))
    return vl

def HParam2Dict(hparam):
    flag = False
    tparam = ''
    for s in hparam:
        if s == '(' or s == '[':
            flag = True
        elif s == ')' or s == ']':
            flag = False
        if flag and s == ',':
            tparam += '$'
        else:
            tparam += s
    lparam = tparam.replace('\n', '').replace('\r', '').replace(' ', '').split(',')
    dparam = {}
    for ss in lparam:
        if ss:
            item = ss.split('=')
            if item[1] == 'True':
                dparam[item[0]] = True
            elif item[1] == 'False':
                dparam[item[0]] = False
            elif item[1].startswith('"') and item[1].endswith('"'):
                dparam[item[0]] = item[1].strip('"')
            elif item[1].startswith("'") and item[1].endswith("'"):
                dparam[item[0]] = item[1].strip("'")
            elif item[1].startswith('(') and item[1].endswith(')'):
                dparam[item[0]] = tuple(GetValueList(item[1]))
            elif item[1].startswith('[') and item[1].endswith(']'):
                dparam[item[0]] = GetValueList(item[1])
            elif item[1].isdecimal():
                dparam[item[0]] = int(item[1])
            else:
                dparam[item[0]] = float(item[1])
    return dparam

def Dict2HParam(dparam):
    params = []
    for key, value in dparam.items():
        item = '{0}={1}'.format(key, value)
        params.append(item)
    return ', '.join(params)

def RegressionModel(dparam, scaler, pca, n_components, method):
    pipeline = []
    if scaler == 1:
        pipeline.append(('minmax', MinMaxScaler()))
    elif scaler == 2:
        pipeline.append(('standard', StandardScaler()))
    if pca:
        pipeline.append(('pca', PCA(n_components=n_components)))
    if method == 0:
        pipeline.append(('linear', LinearRegression(**dparam)))
    elif method == 1:
        pipeline.append(('ridge', Ridge(**dparam)))
    elif method == 2:
        pipeline.append(('lasso', Lasso(**dparam)))
    elif method == 3:
        pipeline.append(('elasticnet', ElasticNet(**dparam)))
    elif method == 4:
        pipeline.append(('gpr', GaussianProcessRegressor(**dparam)))
    elif method == 5:
        pipeline.append(('knr', KNeighborsRegressor(**dparam)))
    elif method == 6:
        pipeline.append(('rfr', RandomForestRegressor(**dparam)))
    elif method == 7:
        pipeline.append(('gbr', GradientBoostingRegressor(**dparam)))
    elif method == 8:
        pipeline.append(('svr', SVR(**dparam)))
    elif method == 9:
        pipeline.append(('mlpr', MLPRegressor(max_iter=1000, **dparam)))
    elif method == 10:
        pipeline.append(('xgb', XGBRegressor(**dparam)))
    elif method == 11:
        pipeline.append(('lgbm', LGBMRegressor(importance_type='gain', verbose=-1, **dparam)))
    return Pipeline(pipeline)

def RegressionCoef(model, method):
    if method == 0:
         return {'coef': model['linear'].coef_.tolist()}
    elif method == 1:
        return {'coef': model['ridge'].coef_.tolist()}
    elif method == 2:
        return {'coef': model['lasso'].coef_.tolist()}
    elif method == 3:
        return {'coef': model['elasticnet'].coef_.tolist()}
    elif method == 4:
        return {}
    elif method == 5:
        return {}
    elif method == 6:
        return {'importances': model['rfr'].feature_importances_.tolist()}
    elif method == 7:
        return {'importances': model['gbr'].feature_importances_.tolist()}
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

class RegressionObjective:
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
        if self.method == 0: # Linear
            pass
        elif self.method == 1: # Ridge
            param['alpha'] = trial.suggest_float('alpha', 0.01, 5, log=True)
        elif self.method == 2: # Losso
            param['alpha'] = trial.suggest_float('alpha', 0.01, 5, log=True)
        elif self.method == 3: # ElasticNet
            param['alpha'] = trial.suggest_float('alpha', 0.01, 5, log=True)
            param['l1_ratio'] = trial.suggest_float('l1_ratio', 0.0, 1.0)
        elif self.method == 4: # GaussianProcess
            param['alpha'] = trial.suggest_float('alpha', 1.0e-10, 1, log=True)
        elif self.method == 5: # KNeighbors
            param['n_neighbors'] = trial.suggest_int('n_neighbors', 1, len(self.Y) / 2)
        elif self.method == 6: # RandomForest
            param['n_estimators'] = trial.suggest_int('n_estimators', 10, 200)
        elif self.method == 7: # GradientBoosting
            param['n_estimators'] = trial.suggest_int('n_estimators', 10, 200)
            param['learning_rate'] = trial.suggest_float('learning_rate', 0.01, 5)
        elif self.method == 8: # SVC
            param['C'] = trial.suggest_float('C', 1e-5, 1e5, log=True)
            param['epsilon'] = trial.suggest_float('epsilon', 0.01, 10)
        elif self.method == 9:  # MLPR
            param['alpha'] = trial.suggest_float('alpha', 0.0001, 0.01, log=True)
        elif self.method == 10:  # XGBoost
            param['eta'] = trial.suggest_float('eta', 0.0, 1.0)
        elif self.method == 11:  # LightGBM
            param['learning_rate'] = trial.suggest_float('learning_rate', 0.0, 1.0)
        model = RegressionModel(param, self.scaler, self.pca, self.n_components, self.method)
        if self.random:
            kf = KFold(n_splits=self.nsplits, shuffle=True, random_state=self.random)
        else:
            kf = KFold(n_splits=self.nsplits)
        scores = []
        for train, test in kf.split(self.X, self.Y):
            xtrain, ytrain = self.X[train], self.Y[train]
            xtest, ytest = self.X[test], self.Y[test]
            model.fit(xtrain, ytrain)
            ypred = model.predict(self.X[test])
            scores.append(mean_squared_error(ytest, ypred))
        if trial.should_prune():
            raise optuna.structs.TrialPruned()
        return -np.mean(scores)

def Optimize(features, obj, dparam, scaler, pca, n_components, method, nsplits, random, ntrials):
    study = optuna.create_study(direction='maximize')
    objective = RegressionObjective(features, obj, dparam, scaler, pca,
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

def Accuracy(id, ytrain, ptrain, ytest, ptest):
    if ytest is not None:
        return {
            'id': id,
            'r2_train': r2_score(ytrain, ptrain),
            'rmse_train': np.sqrt(mean_squared_error(ytrain, ptrain)),
            'mae_train': mean_absolute_error(ytrain, ptrain),
            'r2_test': r2_score(ytest, ptest),
            'rmse_test': np.sqrt(mean_squared_error(ytest, ptest)),
            'mae_test': mean_absolute_error(ytest, ptest)
        }
    else:
        return {
            'id': id,
            'r2_train': r2_score(ytrain, ptrain),
            'rmse_train': np.sqrt(mean_squared_error(ytrain, ptrain)),
            'mae_train': mean_absolute_error(ytrain, ptrain)
        }

def AccuracyMaen(accuracies):
    df = pd.DataFrame(accuracies)
    return {
        'id': -1,
        'r2_train': df['r2_train'].mean(),
        'rmse_train': df['rmse_train'].mean(),
        'mae_train': df['mae_train'].mean(),
        'r2_test': df['r2_test'].mean(),
        'rmse_test': df['rmse_test'].mean(),
        'mae_test': df['mae_test'].mean()
    }

def RegressionExec(features, obj, hparam, optimize, testsize, randomts, scaler,
                   pca, n_components, method, nsplits, random, ntrials, columns, task_id):
    features = np.array(features)
    obj = np.array(obj)
    if testsize > 0.0 and testsize <= 0.5:
        if randomts:
            features, test_features, obj, test_obj = train_test_split(features, obj, test_size=testsize, random_state=randomts)
        else:
            features, test_features, obj, test_obj = train_test_split(features, obj, test_size=testsize)
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
    model = RegressionModel(dparam, scaler, pca, n_components, method)
    if random:
        kf = KFold(n_splits=nsplits, shuffle=True, random_state=random)
    else:
        kf = KFold(n_splits=nsplits)
    accuracies = []
    predictions = {'Objective': obj.tolist()}
    for i, (train, test) in enumerate(kf.split(features, obj)):
        xtrain, ytrain = features[train], obj[train]
        xtest, ytest = features[test], obj[test]
        model.fit(xtrain, ytrain)
        pred = model.predict(features)
        predictions['Predict%d' % i] = pred.tolist()
        flag = np.full(len(pred), False)
        flag[test] = True
        predictions['Test%d' % i] = flag.tolist()
        accuracies.append(Accuracy(i, ytrain, pred[train], ytest, pred[test]))
    accuracies.append(AccuracyMaen(accuracies))
    # train
    model.fit(features, obj)
    pred = model.predict(features)
    predictions['PredictAll'] = pred.tolist()
    if test_features is not None:
        test_pred = model.predict(test_features)
        ldiff = len(obj) - len(test_obj)
        predictions['ObjectiveTest'] = test_obj.tolist()
        predictions['ObjectiveTest'].extend([None] * ldiff)
        predictions['PredictTest'] = test_pred.tolist()
        predictions['PredictTest'].extend([None] * ldiff)
        accuracies.append(Accuracy(-2, obj, pred, test_obj, test_pred))
    else:
        accuracies.append(Accuracy(-2, obj, pred, None, None))
    coef = RegressionCoef(model, method)
    if pca:
        columns = ['PC{}'.format(i) for i in range(1, n_components + 1)]
    results = {
        'accuracies': accuracies,
        'columns': columns,
        'trials': trials,
        **coef
    }
    reg = Regression.objects.get(task_id=task_id)
    reg.hparam = hparam
    pdf = pd.DataFrame(predictions)
    reg.save_csv(pdf)
    reg.save_model(model)
    reg.results = json.dumps(results)
    reg.save()

def RegreSHAPExec(model_data, features, obj, columns, use_kernel, kmeans, nsample,  task_id):
    buf = BytesIO(model_data)
    buf.write(model_data)
    model = joblib.load(buf)
    buf.close()
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
    if use_kernel or method == 'gpr' or method == 'knr' or method == 'svr' or method == 'mlpr':
        summary = shap.kmeans(features, kmeans)
        explainer = shap.KernelExplainer(model[step].predict, summary)
        if nsample < obj.shape[0]:
            x_test = features[:nsample]
        else:
            x_test = features
    elif method == 'linear' or method == 'ridge' or method == 'lasso' or method == 'elasticnet':
        explainer = shap.LinearExplainer(model[step], features)
        x_test = features
    elif method == 'rfr' or method == 'gbr' or method == 'xgb' or method == 'lgbm':
        explainer = shap.TreeExplainer(model[step])
        x_test = features
    shap_values = explainer.shap_values(X=x_test)
    results = {
        'shap_values': shap_values.tolist(),
        'x_test': x_test.tolist(),
        'columns': columns
    }
    model = RegreSHAP.objects.get(task_id=task_id)
    model.results = json.dumps(results)
    model.save()

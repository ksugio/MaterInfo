from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from skl2onnx import convert_sklearn, update_registered_converter
from skl2onnx.common.data_types import FloatTensorType
from skl2onnx.common.shape_calculator import calculate_linear_regressor_output_shapes
from onnxmltools.convert.xgboost.operator_converters.XGBoost import convert_xgboost
from onnxmltools.convert.lightgbm.operator_converters.LightGbm import convert_lightgbm
from onnxruntime import InferenceSession
import numpy as np
import optuna

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
            xtrain, ytrain = self.X.iloc[train], self.Y.iloc[train]
            xtest, ytest = self.X.iloc[test], self.Y.iloc[test]
            model.fit(xtrain, ytrain)
            ypred = model.predict(self.X.iloc[test])
            scores.append(mean_squared_error(ytest, ypred))
        if trial.should_prune():
            raise optuna.structs.TrialPruned()
        return -np.mean(scores)

def ToONNX(method, model, ncol):
    if method == 10:
        update_registered_converter(
            XGBRegressor,
            "XGBoostXGBRegressor",
            calculate_linear_regressor_output_shapes,
            convert_xgboost,
        )
        onx = convert_sklearn(
            model,
            "pipeline_xgboost",
            [("input", FloatTensorType([None, ncol]))],
            target_opset={"": 12, "ai.onnx.ml": 2},
        )
    elif method == 11:
        update_registered_converter(
            LGBMRegressor,
            "LightGbmLGBMRegressor",
            calculate_linear_regressor_output_shapes,
            convert_lightgbm,
            #options={"split": None},
        )
        onx = convert_sklearn(
            model,
            "pipeline_lightgbm",
            [("input", FloatTensorType([None, ncol]))],
            target_opset={"": 14, "ai.onnx.ml": 2}
        )
    else:
        onx = convert_sklearn(
            model,
            initial_types=[('input', FloatTensorType([None, ncol]))]
        )
    return onx.SerializeToString()

def RunONNX(onxs, values):
    sess = InferenceSession(onxs)
    input_name = sess.get_inputs()[0].name
    pred_onx = sess.run(None, {input_name: values.astype(np.float32)})[0]
    return pred_onx.reshape(-1)

def TrainModel(x_train, y_train, dparam, method):
    if method == 0:
        model = LinearRegression(**dparam)
    elif method == 1:
        model = Ridge(**dparam)
    elif method == 2:
        model = Lasso(**dparam)
    elif method == 3:
        model = ElasticNet(**dparam)
    elif method == 4:
        model = GaussianProcessRegressor(**dparam)
    elif method == 5:
        model = KNeighborsRegressor(**dparam)
    elif method == 6:
        model = RandomForestRegressor(**dparam)
    elif method == 7:
        model = GradientBoostingRegressor(**dparam)
    elif method == 8:
        model = SVR(**dparam)
    elif method == 9:
        model = MLPRegressor(max_iter=1000, **dparam)
    elif method == 10:
        model = XGBRegressor(**dparam)
    elif method == 11:
        model = LGBMRegressor(importance_type='gain', verbose=-1, **dparam)
    model.fit(x_train, y_train)
    return model

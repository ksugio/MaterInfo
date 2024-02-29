from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import KFold
from sklearn.metrics import f1_score
from sklearn.linear_model import RidgeClassifier, LogisticRegression
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import LinearSVC, SVC
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from skl2onnx import convert_sklearn, update_registered_converter
from skl2onnx.common.data_types import FloatTensorType
from skl2onnx.common.shape_calculator import calculate_linear_classifier_output_shapes
from onnxmltools.convert.xgboost.operator_converters.XGBoost import convert_xgboost
from onnxmltools.convert.lightgbm.operator_converters.LightGbm import convert_lightgbm
from onnxruntime import InferenceSession
from .regression_lib import HParam2Dict
import numpy as np
import optuna

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
            kf = KFold(n_splits=self.nsplits, shuffle=True, random_state=self.random)
        else:
            kf = KFold(n_splits=self.nsplits)
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

def ToONNX(method, model, ncol):
    if method == 10:
        update_registered_converter(
            XGBClassifier,
            "XGBoostXGBClassifier",
            calculate_linear_classifier_output_shapes,
            convert_xgboost,
            options={"nocl": [True, False], "zipmap": [True, False, "columns"]},
        )
        onx = convert_sklearn(
            model,
            "pipeline_xgboost",
            [("input", FloatTensorType([None, ncol]))],
            target_opset={"": 12, "ai.onnx.ml": 2},
        )
    elif method == 11:
        update_registered_converter(
            LGBMClassifier,
            "LightGbmLGBMClassifier",
            calculate_linear_classifier_output_shapes,
            convert_lightgbm,
            options={"nocl": [True, False], "zipmap": [True, False, "columns"]},
        )
        onx = convert_sklearn(
            model,
            "pipeline_lightgbm",
            [("input", FloatTensorType([None, ncol]))],
            target_opset={"": 12, "ai.onnx.ml": 2}
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
        model = RidgeClassifier(**dparam)
    elif method == 1:
        model = LogisticRegression(max_iter=1000, **dparam)
    elif method == 2:
        model = GaussianProcessClassifier(**dparam)
    elif method == 3:
        model = GaussianNB(**dparam)
    elif method == 4:
        model = KNeighborsClassifier(**dparam)
    elif method == 5:
        model = RandomForestClassifier(**dparam)
    elif method == 6:
        model = GradientBoostingClassifier(**dparam)
    elif method == 7:
        model = LinearSVC(**dparam)
    elif method == 8:
        model = SVC(**dparam)
    elif method == 9:
        model = MLPClassifier(max_iter=1000, **dparam)
    elif method == 10:
        model = XGBClassifier(**dparam)
    elif method == 11:
        model = LGBMClassifier(importance_type='gain', verbose=-1, **dparam)
    model.fit(x_train, y_train)
    return model

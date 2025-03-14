from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, Task, ModelUploadTo, Unique
from .filter import Filter
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from skl2onnx import convert_sklearn, update_registered_converter
from skl2onnx.common.data_types import FloatTensorType
from skl2onnx.common.shape_calculator import calculate_linear_regressor_output_shapes
from onnxmltools.convert.xgboost.operator_converters.XGBoost import convert_xgboost
from onnxmltools.convert.lightgbm.operator_converters.LightGbm import convert_lightgbm
from onnxruntime import InferenceSession
from io import BytesIO
import numpy as np
import pandas as pd
import json
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def ToONNX(method, model, ncol):
    if method == 'xgb':
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
    elif method == 'lgbm':
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
    input_shape = sess.get_inputs()[0].shape
    if input_shape[1] == values.shape[1]:
        pred_onx = sess.run(None, {input_name: values.astype(np.float32)})[0]
        return pred_onx.reshape(-1)
    else:
        return None

class Regression(Created, Updated, Remote, Task, Unique):
    upper = models.ForeignKey(Filter, verbose_name='Filter', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    testsize = models.FloatField(verbose_name='Test Size', default=0.0)
    randomts = models.PositiveIntegerField(verbose_name='Test random state', blank=True, null=True)
    ScalerChoices = ((0, 'None'), (1, 'MinMax'), (2, 'Standard'))
    scaler = models.PositiveSmallIntegerField(verbose_name='Scaler', choices=ScalerChoices, default=0)
    pca = models.BooleanField(verbose_name='PCA', default=False)
    n_components = models.PositiveSmallIntegerField(verbose_name='PCA n_components', default=8)
    MethodChoices = ((0, 'Linear'), (1, 'Ridge'), (2, 'Lasso'), (3, 'ElasticNet'), (4, 'GaussianProcess'),
                     (5, 'KNeighbors'), (6, 'RandomForest'), (7, 'GradientBoosting'), (8, 'SVR'), (9, 'MLPR'),
                     (10, 'XGBoost'), (11, 'LightGBM'))
    method = models.PositiveSmallIntegerField(verbose_name='Method', choices=MethodChoices, default=0)
    hparam = models.TextField(verbose_name='Hyperparameter', blank=True)
    objective = models.CharField(verbose_name='Objective', max_length=50)
    drop = models.CharField(verbose_name='Drop columns', max_length=250, blank=True)
    nsplits = models.PositiveSmallIntegerField(verbose_name='Number of splits', default=5)
    random = models.PositiveIntegerField(verbose_name='Split random state', blank=True, null=True)
    ntrials = models.PositiveIntegerField(verbose_name='Number of trials', default=20)
    nplot = models.PositiveSmallIntegerField(verbose_name='Number of plot features', default=10)
    file = models.FileField(verbose_name='Prediction file', upload_to=ModelUploadTo, blank=True, null=True)
    file2 = models.FileField(verbose_name='Model file', upload_to=ModelUploadTo, blank=True, null=True)
    File2TypeChoices = ((0, 'joblib'), (1, 'onnx'))
    file2_type = models.PositiveSmallIntegerField(verbose_name='File2 type', choices=File2TypeChoices, default=0)
    results = models.TextField(verbose_name='JSON Results', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('collect:regression_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('collect:regression_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('collect:regression_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('collect:regression_delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('collect:api_regression_update', kwargs={'pk': self.id})

    def recent_updated_at(self):
        updated_at = self.upper.recent_updated_at()
        if self.updated_at > updated_at:
            updated_at = self.updated_at
        return updated_at

    def save_csv(self, df):
        buf = BytesIO()
        df.to_csv(buf, index=False, mode="wb", encoding='UTF-8')
        self.file.save('Regression.csv', buf, save=False)
        buf.close()

    def read_csv(self):
        if self.file:
            with self.file.open('r') as f:
                return pd.read_csv(f)
        return None

    def save_model(self, model):
        buf = BytesIO()
        joblib.dump(model, buf)
        self.file2.save('RegressionModel.joblib', buf, save=False)
        buf.close()
        self.file2_type = 0

    def read_model(self, raw_data=False):
        with self.file2.open('rb') as f:
            if raw_data:
                return f.read()
            else:
                return joblib.load(f)

    def get_n_components(self, features):
        if self.n_components < features.shape[1]:
            return self.n_components
        else:
            return features.shape[1]

    def drop_columns(self, df):
        ldrop = self.drop.replace('\n', '').replace('\r', '').replace(' ', '').split(',')
        cols = []
        for col in ldrop:
            if col in df.columns:
                cols.append(col)
        return df.drop(columns=cols)

    def dataset(self, shuffle=False):
        df = self.upper.check_read_csv()
        if df is None:
            return None, None
        if df.isnull().values.sum() > 0:
            return None, None
        if self.objective not in df.columns:
            return None, None
        if shuffle:
            df = df.sample(frac=1, ignore_index=True)
        features = self.upper.upper.drophead(df)
        obj = features.pop(self.objective)
        features = self.drop_columns(features)
        return features, obj

    def to_onnx(self):
        model = self.read_model()
        method = model.steps[-1][0]
        features, obj = self.dataset()
        pred = model.predict(features.values)
        onnx = ToONNX(method, model, features.shape[1])
        pred_onnx = RunONNX(onnx, features.values)
        mse_onnx = mean_squared_error(pred_onnx, pred)
        return onnx, mse_onnx

    def plot(self, **kwargs):
        pdf = self.read_csv()
        if pdf is None:
            return
        obj = pdf['Objective']
        pid = kwargs['pid']
        if 'Predict%d' % pid not in pdf.columns:
            return
        pred = pdf['Predict%d' % pid]
        if len(obj) != len(pred):
            return
        test = pdf['Test%d' % pid]
        train = np.bitwise_not(test)
        total = pd.concat([obj, pred])
        tmin = total.min()
        tmax = total.max()
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.axline((0, 0), slope=1, color='black', linewidth=1)
        ax.plot(obj[train], pred[train], '.', label='Train')
        ax.plot(obj[test], pred[test], '.', label='Test')
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlim(tmin, tmax)
        ax.set_ylim(tmin, tmax)
        ax.set_xlabel(self.objective)
        ax.legend(loc="lower right")
        ax.set_ylabel('Predicted ' + self.objective)
        return fig

    def plot_all(self, **kwargs):
        pdf = self.read_csv()
        if pdf is None:
            return
        obj = pdf['Objective']
        if 'PredictAll' not in pdf.columns:
           return
        pred = pdf['PredictAll']
        if len(obj) != len(pred):
            return
        total = pd.concat([obj, pred])
        tmin = total.min()
        tmax = total.max()
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.axline((0, 0), slope=1, color='black', linewidth=1)
        if 'ObjectiveTest' in pdf.columns and 'PredictTest' in pdf.columns:
            ax.plot(obj, pred, '.', label='Train')
            ax.plot(pdf['ObjectiveTest'], pdf['PredictTest'], '.', label='Test')
            ax.legend(loc="lower right")
        else:
            ax.plot(obj, pred, '.')
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlim(tmin, tmax)
        ax.set_ylim(tmin, tmax)
        ax.set_xlabel(self.objective)
        ax.set_ylabel('Predicted ' + self.objective)
        return fig

    def plot_importance(self, **kwargs):
        results = json.loads(self.results)
        if 'coef' in results:
            fig, ax = plt.subplots()
            name, value = self.sortcoef(results['columns'], results['coef'])
            ax.bar(name, value)
            ax.set_ylabel('Coefficients')
            ax.xaxis.set_tick_params(rotation=90)
            return fig
        elif 'importances' in results:
            fig, ax = plt.subplots()
            name, value = self.sortcoef(results['columns'], results['importances'])
            ax.bar(name, value)
            ax.set_ylabel('Importances')
            ax.xaxis.set_tick_params(rotation=90)
            return fig

    def sortcoef(self, columns, coef):
        data = list(zip(columns, coef))
        data = sorted(data, key=lambda x: abs(x[1]), reverse=True)[:self.nplot]
        return zip(*data)

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
                ax.set_ylabel('Negative MSE')
                return fig

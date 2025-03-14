from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, Task, ModelUploadTo, Unique
from .filter import Filter
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from skl2onnx import convert_sklearn, update_registered_converter
from skl2onnx.common.data_types import FloatTensorType
from skl2onnx.common.shape_calculator import calculate_linear_classifier_output_shapes
from onnxmltools.convert.xgboost.operator_converters.XGBoost import convert_xgboost
from onnxmltools.convert.lightgbm.operator_converters.LightGbm import convert_lightgbm
from onnxruntime import InferenceSession
from io import BytesIO
import numpy as np
import json
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def ToONNX(method, model, ncol):
    if method == 'xgb':
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
    elif method == 'lgbm':
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

class Classification(Created, Updated, Remote, Task, Unique):
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
    n_components = models.PositiveSmallIntegerField(verbose_name='Number of components', default=8)
    MethodChoices = ((0, 'Ridge'), (1, 'Logistic'), (2, 'GaussianProcess'), (3, 'GaussianNB'), (4, 'KNeighbors'),
                     (5, 'RandomForest'), (6, 'GradientBoosting'), (7, 'LinearSVC'), (8, 'SVC'), (9, 'MLPC'),
                     (10, 'XGBoost'), (11, 'LightGBM'))
    method = models.PositiveSmallIntegerField(verbose_name='Method', choices=MethodChoices, default=0)
    hparam = models.TextField(verbose_name='Hyperparameter', blank=True)
    objective = models.CharField(verbose_name='Objective', max_length=50)
    drop = models.CharField(verbose_name='Drop columns', max_length=250, blank=True)
    nsplits = models.PositiveSmallIntegerField(verbose_name='Number of splits', default=5)
    random = models.PositiveIntegerField(verbose_name='Split random state', blank=True, null=True)
    ntrials = models.PositiveIntegerField(verbose_name='Number of trials', default=20)
    nplot = models.PositiveSmallIntegerField(verbose_name='Number of plot features', default=10)
    file = models.FileField(verbose_name='Model file', upload_to=ModelUploadTo, blank=True, null=True)
    FileTypeChoices = ((0, 'joblib'), (1, 'onnx'))
    file_type = models.PositiveSmallIntegerField(verbose_name='File type', choices=FileTypeChoices, default=0)
    results = models.TextField(verbose_name='JSON Results', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('collect:classification_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('collect:classification_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('collect:classification_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('collect:classification_delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('collect:api_classification_update', kwargs={'pk': self.id})

    def recent_updated_at(self):
        updated_at = self.upper.recent_updated_at()
        if self.updated_at > updated_at:
            updated_at = self.updated_at
        return updated_at

    def save_model(self, model):
        buf = BytesIO()
        joblib.dump(model, buf)
        self.file.save('ClassificationModel.joblib', buf, save=False)
        buf.close()
        self.file_type = 0

    def read_model(self, raw_data=False):
        with self.file.open('rb') as f:
            if raw_data:
                return f.read()
            else:
                return joblib.load(f)

    def get_n_components(self, features):
        if self.n_components < len(features.columns):
            return self.n_components
        else:
            return len(features.columns)

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
        obj = df.pop(self.objective)
        features = self.upper.upper.drophead(df)
        features = self.drop_columns(features)
        return features, obj

    def check_obj(self, obj):
        if self.method == 7 and obj.dtype == 'object':
            return False
        elif self.method == 8 and obj.dtype == 'object':
            return False
        elif self.method == 10 and obj.dtype == 'object':
            return False
        else:
            return True

    def to_onnx(self):
        model = self.read_model()
        method = model.steps[-1][0]
        features, obj = self.dataset()
        pred = model.predict(features.values)
        onnx = ToONNX(method, model, features.shape[1])
        pred_onnx = RunONNX(onnx, features.values)
        score_onnx = accuracy_score(pred_onnx, pred)
        return onnx, score_onnx

    def plot_importance(self, **kwargs):
        if self.results:
            results = json.loads(self.results)
            if 'importances' in results:
                fig, ax = plt.subplots()
                data = list(zip(results['columns'], results['importances']))
                data = sorted(data, key=lambda x: x[1], reverse=True)[:self.nplot]
                name, value = zip(*data)
                ax.bar(name, value)
                ax.set_ylabel('Importances')
                ax.xaxis.set_tick_params(rotation=90)
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
                ax.set_ylabel('F1 Score')
                return fig

from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, ModelUploadTo, UniqueID
from .filter import Filter
from .regression_lib import HParam2Dict, Dict2HParam, RegressionModel, RegressionCoef, RegressionObjective, ToONNX, RunONNX
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
from io import BytesIO
import numpy as np
import pandas as pd
import json
import joblib
import optuna
import shap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class Regression(Created, Updated, Remote):
    upper = models.ForeignKey(Filter, verbose_name='Filter', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
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
    random = models.PositiveIntegerField(verbose_name='Random State', blank=True, null=True)
    ntrials = models.PositiveIntegerField(verbose_name='Number of trials', default=20)
    nplot = models.PositiveSmallIntegerField(verbose_name='Number of plot features', default=10)
    file = models.FileField(verbose_name='Prediction file', upload_to=ModelUploadTo, blank=True, null=True)
    file2 = models.FileField(verbose_name='Model file', upload_to=ModelUploadTo, blank=True, null=True)
    file2_type = models.PositiveSmallIntegerField(verbose_name='File2 type', default=0)
    results = models.TextField(verbose_name='JSON Results', blank=True)
    unique = models.CharField(verbose_name='Unique ID', max_length=36, default=UniqueID)

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

    def save_joblib(self, model):
        buf = BytesIO()
        joblib.dump(model, buf)
        self.file2.save('RegressionModel.joblib', buf, save=False)
        buf.close()
        self.file2_type = 0

    def read_joblib(self):
        with self.file2.open('rb') as f:
            return joblib.load(f)

    def save_onnx(self, onxs):
        buf = BytesIO()
        buf.write(onxs)
        self.file2.save('RegressionModel.onnx', buf, save=False)
        buf.close()
        self.file2_type = 1

    def read_onnx(self):
        with self.file2.open('rb') as f:
            return f.read()

    def accuracy(self, id, ytrain, ptrain, ytest, ptest):
        return {
            'id': id,
            'r2_train': r2_score(ytrain, ptrain),
            'rmse_train': mean_squared_error(ytrain, ptrain),
            'mae_train': mean_absolute_error(ytrain, ptrain),
            'r2_test': r2_score(ytest, ptest),
            'rmse_test': mean_squared_error(ytest, ptest),
            'mae_test': mean_absolute_error(ytest, ptest)
        }

    def accuracy_maen(self, accuracies):
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

    def get_n_components(self, features):
        if self.n_components < features.shape[1]:
            return self.n_components
        else:
            return features.shape[1]

    def optimize(self, features, obj, dparam):
        study = optuna.create_study(direction='maximize')
        objective = RegressionObjective(features, obj, dparam, self.scaler,
                                        self.pca, self.get_n_components(features),
                                        self.method, self.nsplits, self.random)
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

    def dataset(self):
        df = self.upper.check_read_csv()
        if df is None:
            return None, None
        if df.isnull().values.sum() > 0:
            return None, None
        if self.objective not in df.columns:
            return None, None
        features = self.upper.upper.drophead(df)
        obj = features.pop(self.objective)
        features = self.drop_columns(features)
        return features, obj

    def test_train(self, optimize):
        features, obj = self.dataset()
        if features is None:
            return
        dparam = HParam2Dict(self.hparam)
        if optimize:
            dparam, trials = self.optimize(features, obj, dparam)
        else:
            trials = {}
        # test with KFold
        model = RegressionModel(dparam, self.scaler, self.pca, self.get_n_components(features), self.method)
        if self.random:
            kf = KFold(n_splits=self.nsplits, shuffle=True, random_state=self.random)
        else:
            kf = KFold(n_splits=self.nsplits)
        accuracies = []
        pdf = pd.DataFrame()
        pdf['Objective'] = obj
        for i, (train, test) in enumerate(kf.split(features, obj)):
            xtrain, ytrain = features.iloc[train], obj.iloc[train]
            xtest, ytest = features.iloc[test], obj.iloc[test]
            model.fit(xtrain, ytrain)
            pred = model.predict(features)
            pdf['Predict%d' % i] = pred
            flag = np.full(len(pred), False)
            flag[test] = True
            pdf['Test%d' % i] = flag
            accuracies.append(self.accuracy(i, ytrain, pred[train], ytest, pred[test]))
        accuracies.append(self.accuracy_maen(accuracies))
        # train
        model.fit(features, obj)
        pred = model.predict(features)
        pdf['PredictAll'] = pred
        onxs = ToONNX(self.method, model, features.shape[1])
        pred_onnx = RunONNX(onxs, features.values)
        mse_onnx = mean_squared_error(pred_onnx, pred)
        coef = RegressionCoef(model, self.method)
        if self.pca:
            columns = ['PC{}'.format(i) for i in range(1, self.get_n_components(features) + 1)]
        else:
            columns = features.columns.tolist()
        results = {
            'accuracies': accuracies,
            'columns': columns,
            'trials': trials,
            **coef
        }
        self.results = json.dumps(results)
        self.save_csv(pdf)
        if mse_onnx > 1e-3:
           self.save_joblib(model)
        else:
           self.save_onnx(onxs)

    def transformed_dataset(self):
        features, obj = self.dataset()
        if features is None:
            return None, None
        columns = features.columns.tolist()
        if self.scaler == 1:
            features = MinMaxScaler().fit_transform(features)
        elif self.scaler == 2:
            features = StandardScaler().fit_transform(features)
        if self.pca:
            n_components = self.get_n_components(features)
            features = PCA(n_components=n_components).fit_transform(features)
            columns = ['PC{}'.format(i) for i in range(1, n_components + 1)]
        if type(features) is np.ndarray:
            features = pd.DataFrame(features, columns=columns)
        return features, obj

    def plot(self, **kwargs):
        pdf = self.read_csv()
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

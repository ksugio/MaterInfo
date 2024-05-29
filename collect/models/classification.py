from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote, ModelUploadTo, Unique
from .filter import Filter
from .regression_lib import HParam2Dict, Dict2HParam
from .classification_lib import ClassificationModel, ClassificationCoef, ClassificationObjective, ToONNX, RunONNX
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
from io import BytesIO
import json
import joblib
import os
import numpy as np
import pandas as pd
import optuna
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class Classification(Created, Updated, Remote, Unique):
    upper = models.ForeignKey(Filter, verbose_name='Filter', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
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
    random = models.PositiveIntegerField(verbose_name='Random State', blank=True, null=True)
    ntrials = models.PositiveIntegerField(verbose_name='Number of trials', default=20)
    nplot = models.PositiveSmallIntegerField(verbose_name='Number of plot features', default=10)
    file = models.FileField(verbose_name='Model file', upload_to=ModelUploadTo, blank=True, null=True)
    file_type = models.PositiveSmallIntegerField(verbose_name='File type', default=0)
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

    def recent_updated_at(self):
        updated_at = self.upper.recent_updated_at()
        if self.updated_at > updated_at:
            updated_at = self.updated_at
        return updated_at

    def save_joblib(self, model):
        buf = BytesIO()
        joblib.dump(model, buf)
        self.file.save('ClassificationModel.joblib', buf, save=False)
        buf.close()
        self.file_type = 0

    def read_joblib(self):
        with self.file.open('rb') as f:
            return joblib.load(f)

    def save_onnx(self, onxs):
        buf = BytesIO()
        buf.write(onxs)
        self.file.save('ClassificationModel.onnx', buf, save=False)
        buf.close()
        self.file_type = 1

    def read_onnx(self):
        with self.file.open('rb') as f:
            return f.read()

    def get_n_components(self, features):
        if self.n_components < len(features.columns):
            return self.n_components
        else:
            return len(features.columns)

    def optimize(self, features, obj, dparam):
        study = optuna.create_study(direction='maximize')
        objective = ClassificationObjective(features.values, obj.values, dparam, self.scaler,
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

    def test_train(self, optimize):
        features, obj = self.dataset()
        if features is None:
            return
        if not self.check_obj(obj):
            return
        dparam = HParam2Dict(self.hparam)
        if optimize:
            dparam, trials = self.optimize(features, obj, dparam)
        else:
            trials = {}
        # test with KFold
        model = ClassificationModel(dparam, self.scaler, self.pca, self.get_n_components(features), self.method)
        if self.random:
            kf = KFold(n_splits=self.nsplits, shuffle=True, random_state=self.random)
        else:
            kf = KFold(n_splits=self.nsplits)
        reports = []
        for i, (train, test) in enumerate(kf.split(features, obj)):
            xtrain, ytrain = features.iloc[train], obj.iloc[train]
            xtest, ytest = features.iloc[test], obj.iloc[test]
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
        if self.method == 10:
            model.fit(features.values, obj)
        else:
            model.fit(features, obj)
        pred = model.predict(features)
        onxs = ToONNX(self.method, model, features.shape[1])
        pred_onnx = RunONNX(onxs, features.values)
        score_onnx = accuracy_score(pred_onnx, pred)
        coef = ClassificationCoef(model, self.method)
        if self.pca:
            columns = ['PC{}'.format(i) for i in range(1, self.get_n_components(features) + 1)]
        else:
            columns = features.columns.tolist()
        results = {
            'reports': reports,
            'mean_accuracy': mean_accuracy,
            'mean_train_accuracy': mean_train_accuracy,
            'columns': columns,
            'trials': trials,
            **coef
        }
        self.results = json.dumps(results)
        if score_onnx < 1.0:
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

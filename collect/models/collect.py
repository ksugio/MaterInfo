from django.utils.module_loading import import_string
from django.db import models
from django.urls import reverse
from config.settings import COLLECT_FEATURES
from project.models import Created, Updated, RemoteRoot, Project, ModelUploadTo
from io import BytesIO
import os
import pandas as pd
import json

HeadColumns = [
    ('Project_id', 0), ('Project_title', '-'),
    ('Sample_id', 0), ('Sample_title', '-'),
    ('Image_id', 0), ('Image_title', '-'),
    ('Image_Filter_id', 0),
    ('Image_Predict_id', 0),
    ('Value_id', 0), ('Value_title', '-'),
    ('Value_Filter_id', 0),
    ('Upper_id', 0),
    ('Model', '-'), ('Model_id', 0),
    ('Category', '-')
]

def CollectUploadTo(instance, filename):
    return filename

class Collect(Created, Updated, RemoteRoot):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    projectids = models.CharField(verbose_name='Other Project IDs', max_length=100, blank=True)
    disp_head = models.PositiveIntegerField(verbose_name='Display Head', default=50)
    disp_tail = models.PositiveIntegerField(verbose_name='Display Tail', default=50)
    file = models.FileField(verbose_name='Feature file', upload_to=ModelUploadTo, blank=True, null=True)
    columns_text = models.TextField(verbose_name='Columns Text', blank=True)
    overview_text = models.TextField(verbose_name='Overview Text', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('collect:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('collect:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('collect:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('collect:delete', kwargs={'pk': self.id})

    def get_table_url(self):
        return reverse('collect:table', kwargs={'pk': self.id, 'name': 'Total'})

    def save_csv(self, df):
        buf = BytesIO()
        df.to_csv(buf, index=False, mode="wb", encoding='UTF-8')
        self.file.save('Collect.csv', buf, save=False)
        buf.close()

    def read_csv(self):
        if self.file:
            with self.file.open('r') as f:
                return pd.read_csv(f)
        return None

    def disp_table(self, **kwargs):
        df = self.read_csv()
        model_name = kwargs['name']
        if 'Model' in df.columns and model_name in df['Model'].values:
            df = df.query('Model == "%s"' % model_name).dropna(how='all', axis=1)
            if 'Image_id' in df.columns and df['Image_id'].sum() == 0:
                df = df.drop(['Image_id', 'Image_title', 'Image_Filter_id'], axis=1)
            if 'Value_id' in df.columns and df['Value_id'].sum() == 0:
                df = df.drop(['Value_id', 'Value_title', 'Value_Filter_id'], axis=1)
            if 'Image_Predict_id' in df.columns and df['Image_Predict_id'].sum() == 0:
                df = df.drop(['Image_Predict_id'], axis=1)
        if df is not None and self.disp_head + self.disp_tail < df.shape[0]:
            return pd.concat([df.head(self.disp_head), df.tail(self.disp_tail)])
        else:
            return df

    def collect_project_features(self, project):
        dfall = None
        for item in COLLECT_FEATURES:
            cls = import_string(item['Model'])
            if hasattr(cls, 'feature'):
                if item['Depth'] == 2:
                    features = cls.objects.filter(upper__upper=project)
                elif item['Depth'] == 3:
                    features = cls.objects.filter(upper__upper__upper=project)
                elif item['Depth'] == 4:
                    features = cls.objects.filter(upper__upper__upper__upper=project)
                ser = []
                for feature in features:
                    feat = feature.feature()
                    if feat:
                        ser.append(pd.Series(feat))
                if ser:
                    df = pd.concat(ser, axis=1)
                    if dfall is not None:
                        dfall = pd.merge(dfall, df, left_index=True, right_index=True, how='outer')
                        dfall.columns = pd.Index(range(dfall.shape[1]))
                    else:
                        dfall = df
        return dfall

    def collect_projects(self, user):
        if self.projectids:
            ids = []
            for sid in self.projectids.split(','):
                try:
                    ids.append(int(sid))
                except:
                    pass
            ids.insert(0, self.upper.id)
            return Project.objects.filter(member=user).filter(id__in=ids)
        else:
            return Project.objects.filter(id=self.upper.id)

    def collect_features(self, user):
        projects = self.collect_projects(user)
        dfall = None
        for project in projects:
            df = self.collect_project_features(project)
            if dfall is not None:
                dfall = pd.merge(dfall, df, left_index=True, right_index=True, how='outer')
                dfall.columns = pd.Index(range(dfall.shape[1]))
            else:
                dfall = df
        if dfall is not None:
            dfall = dfall.dropna(how='all')
            indexes = list(dfall.index.values)
            head = []
            for item in HeadColumns:
                head.append(item[0])
                if item[0] in dfall.index.values:
                    indexes.remove(item[0])
            dfall = dfall.reindex(head + indexes)
            dfall = dfall.T
            dfall = self.sort_features(dfall)
            for item in HeadColumns:
                if item[0] in dfall.columns.values:
                    dfall[item[0]] = dfall[item[0]].fillna(item[1])
            self.columns_text = ','.join(indexes)
            self.overview(dfall)
            self.save_csv(dfall)

    def upload(self, file):
        df = pd.read_csv(file)
        if 'Project_id' not in df.columns:
            df.insert(0, 'Project_id', self.upper.id)
            df.insert(1, 'Project_title', self.upper.title)
        if 'Sample_id' not in df.columns:
            df.insert(2, 'Sample_id', df.index + 1)
        columns = list(df.columns.values)
        for item in HeadColumns:
            if item[0] in df.columns.values:
                columns.remove(item[0])
        self.columns_text = ','.join(columns)
        self.overview(df)
        self.save_csv(df)

    def overview(self, df):
        text = 'Project:%d,' % df['Project_id'].drop_duplicates().shape[0]
        text = '%sSample:%d,' % (text, df['Sample_id'].drop_duplicates().shape[0])
        if 'Image_id' in df:
            text = '%sImage:%d,' % (text, df['Image_id'].drop_duplicates().shape[0] - 1)
        if 'Value_id' in df:
            text = '%sValue:%d,' % (text, df['Value_id'].drop_duplicates().shape[0] - 1)
        if 'Model' in df:
            model = df['Model']
            for item in model.drop_duplicates():
                text = '%s%s:%d,' % (text, item, sum(model == item))
            text = '%sTotal:%d,' % (text, model.shape[0])
        self.overview_text = text.rstrip(',')

    def sort_features(self, df):
        sort_keys = ['Project_id', 'Sample_id', 'Image_id', 'Image_Filter_id', 'Value_id', 'Value_Filter_id', 'Model']
        keys = []
        for key in sort_keys:
            if key in df.columns:
                keys.append(key)
        return df.sort_values(keys)

    def drophead(self, df):
        cols = [item[0] for item in HeadColumns if item[0] in df.columns]
        return df.drop(columns=cols)

    def columns_choice(self):
        choice = []
        for item in self.columns_text.split(','):
            choice.append((item, item))
        return choice

    def head_columns(self):
        return [item[0] for item in HeadColumns]

    def project_upper_updated_features(self, project):
        updated = []
        for item in COLLECT_FEATURES:
            cls = import_string(item['Model'])
            if hasattr(cls, 'upper_updated'):
                if item['Depth'] == 2:
                    features = cls.objects.filter(upper__upper=project)
                elif item['Depth'] == 3:
                    features = cls.objects.filter(upper__upper__upper=project)
                elif item['Depth'] == 4:
                    features = cls.objects.filter(upper__upper__upper__upper=project)
                for feature in features:
                    if feature.upper_updated():
                        updated.append(feature)
        return updated

    def upper_updated_features(self, user):
        projects = self.collect_projects(user)
        updated = []
        for project in projects:
            updated.extend(self.project_upper_updated_features(project))
        return updated

    def project_upper_updated_measure_features(self, project):
        for item in COLLECT_FEATURES:
            cls = import_string(item['Model'])
            if hasattr(cls, 'upper_updated_measure'):
                if item['Depth'] == 2:
                    features = cls.objects.filter(upper__upper=project)
                elif item['Depth'] == 3:
                    features = cls.objects.filter(upper__upper__upper=project)
                elif item['Depth'] == 4:
                    features = cls.objects.filter(upper__upper__upper__upper=project)
                for feature in features:
                    feature.upper_updated_measure()

    def upper_updated_measure_features(self, user):
        projects = self.collect_projects(user)
        for project in projects:
            self.project_upper_updated_measure_features(project)

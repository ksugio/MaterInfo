from django.utils.module_loading import import_string
from django.db import models
from django.urls import reverse
from config.settings import COLLECT_FEATURES
from project.models import Created, Updated, Remote, Project, ModelUploadTo, Unique
from io import BytesIO
import pandas as pd
import requests
import os

HeadColumns = [
    ('Project_id', 0), ('Project_title', '-'),
    ('Sample_id', 0), ('Sample_title', '-'),
    ('Image_id', 0), ('Image_title', '-'),
    ('Value_id', 0), ('Value_title', '-'),
    ('Upper_id', 0),
    ('Model', '-'), ('Model_id', 0),
    ('Category', '-')
]

def CollectUploadTo(instance, filename):
    return filename

class Collect(Created, Updated, Remote, Unique):
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

    def get_apiupdate_url(self):
        return reverse('collect:api_update', kwargs={'pk': self.id})

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
                df = df.drop(['Image_id', 'Image_title'], axis=1)
            if 'Value_id' in df.columns and df['Value_id'].sum() == 0:
                df = df.drop(['Value_id', 'Value_title'], axis=1)
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
                    dfall[item[0]] = dfall[item[0]].infer_objects().fillna(item[1])
            self.columns_text = ','.join(indexes)
            self.overview(dfall)
            self.save_csv(dfall)

    def upload_features(self, file, encoding, sheetname):
        fn, ext = os.path.splitext(file.name)
        if ext == '.csv':
            df = pd.read_csv(file, encoding=encoding)
        elif ext == '.xlsx':
            if not sheetname:
                sheetname = 0
            df = pd.read_excel(file, sheet_name=sheetname)
        self.checksave_df(df)

    def checksave_df(self, df):
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

    def get_features(self, url, **kwargs):
        if url.startswith('http'):
            if url.startswith(kwargs['request_host']):
                response = requests.get(url, cookies=kwargs['request_cookies'])
            else:
                response = requests.get(url)
        else:
            response = requests.get(kwargs['request_host'] + url,
                                    cookies=kwargs['request_cookies'])
        try:
            buf = BytesIO(response.content)
            df = pd.read_csv(buf)
            buf.close()
        except:
            return
        self.checksave_df(df)

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

    def project_latest_features(self, project):
        latest = []
        for item in COLLECT_FEATURES:
            cls = import_string(item['Model'])
            if item['Depth'] == 2:
                features = cls.objects.filter(upper__upper=project)
            elif item['Depth'] == 3:
                features = cls.objects.filter(upper__upper__upper=project)
            elif item['Depth'] == 4:
                features = cls.objects.filter(upper__upper__upper__upper=project)
            for feature in features:
                if hasattr(feature, 'upper_updated') and feature.upper_updated():
                    latest.append((feature, True))
                elif feature.updated_at > self.updated_at:
                    latest.append((feature, False))
        return latest

    def latest_features(self, user):
        projects = self.collect_projects(user)
        latest = []
        for project in projects:
            latest.extend(self.project_latest_features(project))
        return latest

    def project_update_upper_updated(self, project):
        for item in COLLECT_FEATURES:
            cls = import_string(item['Model'])
            if hasattr(cls, 'upper_updated') and hasattr(cls, 'measure') :
                if item['Depth'] == 2:
                    features = cls.objects.filter(upper__upper=project)
                elif item['Depth'] == 3:
                    features = cls.objects.filter(upper__upper__upper=project)
                elif item['Depth'] == 4:
                    features = cls.objects.filter(upper__upper__upper__upper=project)
                for feature in features:
                    if feature.upper_updated():
                        feature.measure()
                        feature.save()

    def update_upper_updated(self, user):
        projects = self.collect_projects(user)
        for project in projects:
            self.project_update_upper_updated(project)

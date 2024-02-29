from config.settings import COLLECT_FILTER_PROCESS
from django.utils.module_loading import import_string
from django.db import models
from django.urls import reverse
from project.models import Updated, Remote
from .filter import Filter
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
import numpy as np
import pandas as pd

class Process(Updated, Remote):
    upper = models.ForeignKey(Filter, verbose_name='Filter', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Name', max_length=16, blank=True)
    order = models.SmallIntegerField(verbose_name='Order')

    def title(self):
        return '%s : %s_%d' % (self.upper.title, self.name, self.order)

    def get_detail_url(self):
        return reverse('collect:filter_update', kwargs={'pk': self.upper.id})

    def get_update_url(self):
        pass

    def get_delete_url(self):
        return reverse('collect:process_delete', kwargs={'pk': self.id})

    def get_table_url(self):
        return reverse('collect:process_table', kwargs={'pk': self.id})

    def entity(self):
        if self.name:
            for item in COLLECT_FILTER_PROCESS:
                if item['Model'].split('.')[-1] == self.name:
                    cls = import_string(item['Model'])
                    return cls.objects.get(id=self.id)
        else:
            for item in COLLECT_FILTER_PROCESS:
                cls = import_string(item['Model'])
                obj = cls.objects.filter(id=self.id)
                if obj:
                    return obj[0]

    def process(self, df, **kwargs):
        return self.entity().process(df, **kwargs)

    def disp_table(self, **kwargs):
        df = self.upper.upper.read_csv()
        df, kwargs = self.upper.procval(df, self.id)
        report = {}
        for key, vals in kwargs.items():
            keys = key.split('_')
            if int(keys[0]) == self.id:
                report[keys[1]] = vals
        rdf = pd.DataFrame(report).T
        hdf = df.isnull().any().to_frame(name='IsNull').T
        df = pd.concat([hdf, df])
        ldf = df.isnull().any(axis=1).to_frame(name='IsNull')
        ldf['IsNull']['IsNull'] = hdf.sum(axis=1) > 0
        df = pd.concat([ldf, df], axis=1)
        if df is not None and self.upper.disp_head + self.upper.disp_tail < df.shape[0]:
            return pd.concat([df.head(self.upper.disp_head), df.tail(self.upper.disp_tail)]), rdf
        else:
            return df, rdf

class Fillna(Process):
    GroupbyChoices = ((0, 'Project_id'), (1, 'Sample_id'), (2, 'Image_id'), (3, 'Image_Filter_id'), (4, 'Value_id'), (5, 'Value_Filter_id'))
    groupby = models.PositiveSmallIntegerField(verbose_name='Groupby', choices=GroupbyChoices, default=1)
    start = models.CharField(verbose_name='Start column', max_length=50)
    end = models.CharField(verbose_name='End column', max_length=50)
    MethodChoices = ((0, 'Mean'), (1, 'Median'), (2, 'FBFill'), (3, 'BFFill'))
    method = models.PositiveSmallIntegerField(verbose_name='Method', choices=MethodChoices, default=0)

    def transform_func(self, x):
        if self.method == 0:
            return x.fillna(np.mean(x))
        elif self.method == 1:
            y = np.median(x)
            if np.isnan(y):
                return x.fillna(np.mean(x))
            else:
                return x.fillna(y)
        elif self.method == 2:
            return x.fillna(method='ffill').fillna(method='bfill')
        elif self.method == 3:
            return x.fillna(method='bfill').fillna(method='ffill')

    def process(self, df, **kwargs):
        cols = list(df.columns)
        si = cols.index(self.start)
        ei = cols.index(self.end)
        grpby = self.get_groupby_display()
        for col in cols[si:ei+1]:
            if col in df:
                df[col] = df.groupby(grpby)[col].transform(self.transform_func)
        return df, kwargs

    def get_update_url(self):
        return reverse('collect:fillna_update', kwargs={'pk': self.id})

class Dropna(Process):
    AxisChoices = ((0, 'rows'), (1, 'columns'))
    axis = models.PositiveSmallIntegerField(verbose_name='Axis', choices=AxisChoices, default=0)
    HowChoices = ((0, 'any'), (1, 'all'))
    how = models.PositiveSmallIntegerField(verbose_name='How', choices=HowChoices, default=0)
    thresh = models.PositiveIntegerField(verbose_name='Thresh', blank=True, null=True)

    def process(self, df, **kwargs):
        if self.thresh:
            return df.dropna(axis=self.get_axis_display(), how=self.get_how_display(), thresh=self.thresh), kwargs
        else:
            return df.dropna(axis=self.get_axis_display(), how=self.get_how_display()), kwargs

    def get_update_url(self):
        return reverse('collect:dropna_update', kwargs={'pk': self.id})

class Drop(Process):
    start = models.CharField(verbose_name='Start column', max_length=50)
    end = models.CharField(verbose_name='End column', max_length=50)

    def process(self, df, **kwargs):
        cols = list(df.columns)
        si = cols.index(self.start)
        ei = cols.index(self.end)
        return df.drop(cols[si:ei+1], axis=1), kwargs

    def get_update_url(self):
        return reverse('collect:drop_update', kwargs={'pk': self.id})

class Select(Process):
    MethodChoices = ((0, 'Keep'), (1, 'Drop'))
    method = models.PositiveSmallIntegerField(verbose_name='Method', choices=MethodChoices, default=0)
    columns = models.TextField(verbose_name='Columns', blank=True)

    def process(self, df, **kwargs):
        head = self.upper.upper.head_columns()
        selected = self.columns.split(',')
        cols = []
        if self.method == 0:
            for col in df.columns:
                if col not in head and col not in selected:
                    cols.append(col)
        elif self.method == 1:
            for col in df.columns:
                if col in selected:
                    cols.append(col)
        return df.drop(cols, axis=1), kwargs

    def get_update_url(self):
        return reverse('collect:select_update', kwargs={'pk': self.id})

class Agg(Process):
    GroupbyChoices = ((0, 'Project_id'), (1, 'Sample_id'), (2, 'Image_id'), (3, 'Image_Filter_id'), (4, 'Value_id'), (5, 'Value_Filter_id'))
    groupby = models.PositiveSmallIntegerField(verbose_name='Groupby', choices=GroupbyChoices, default=1)
    MethodChoices = ((0, 'Mean'), (1, 'Median'), (2, 'Min'), (3, 'Max'))
    method = models.PositiveSmallIntegerField(verbose_name='Method', choices=MethodChoices, default=0)

    def agg_func(self, x):
        head = self.upper.upper.head_columns()
        if not x.name in head:
            if self.method == 0:
                return np.mean(x)
            elif self.method == 1:
                y = np.median(x)
                if np.isnan(y):
                    return np.mean(x)
                else:
                    return y
            elif self.method == 2:
                return np.min(x)
            elif self.method == 3:
                return np.max(x)
        else:
            if self.groupby == 0:
                if x.name == 'Sample_id' or x.name == 'Image_id' or x.name == 'Image_Filter_id' or x.name == 'Value_id' or x.name == 'Value_Filter_id' or x.name == 'Model_id':
                    return 0
                elif x.name == 'Sample_title' or x.name == 'Image_title' or x.name == 'Value_title' or x.name == 'Model' or x.name == 'Category':
                    return '-'
            elif self.groupby == 1:
                if x.name == 'Image_id' or x.name == 'Image_Filter_id' or x.name == 'Value_id' or x.name == 'Value_Filter_id' or x.name == 'Model_id':
                    return 0
                elif x.name == 'Image_title' or x.name == 'Value_title' or x.name == 'Model' or x.name == 'Category':
                    return '-'
            elif self.groupby == 2:
                if x.name == 'Image_Filter_id' or x.name == 'Model_id':
                    return 0
                elif x.name == 'Model' or x.name == 'Category':
                    return '-'
            elif self.groupby == 4:
                if x.name == 'Value_Filter_id' or x.name == 'Model_id':
                    return 0
                elif x.name == 'Model' or x.name == 'Category':
                    return '-'
            elif self.groupby == 3 or self.groupby == 5:
                if x.name == 'Model_id':
                    return 0
                elif x.name == 'Model' or x.name == 'Category':
                    return '-'
            return x.iloc[0]

    def process(self, df, **kwargs):
        grpby = self.get_groupby_display()
        bi = df[grpby] > 0
        ndf = df[bi].dropna(how='all', axis=1)
        ndf = ndf.groupby(grpby).agg(self.agg_func)
        ndf = ndf.reset_index()
        df = df.drop(index=df[bi].index)
        if df.empty:
            df = ndf
        else:
            df.append(ndf)
        df = self.upper.upper.sort_features(df)
        df.index = np.arange(len(df))
        return df, kwargs

    def get_update_url(self):
        return reverse('collect:agg_update', kwargs={'pk': self.id})

class Query(Process):
    condition = models.TextField(verbose_name='Condition')

    def process(self, df, **kwargs):
        try:
            return df.query(self.condition), kwargs
        except:
            return df, kwargs

    def get_update_url(self):
        return reverse('collect:query_update', kwargs={'pk': self.id})

class Exclude(Process):
    percentile = models.FloatField(verbose_name='Percentile')
    Choices = ((0, 'Greater'), (1, 'Smaller'))
    condition = models.PositiveSmallIntegerField(verbose_name='Condition', choices=Choices, default=0)
    start = models.CharField(verbose_name='Start column', max_length=50)
    end = models.CharField(verbose_name='End column', max_length=50)

    def process(self, df, **kwargs):
        cols = list(df.columns)
        si = cols.index(self.start)
        ei = cols.index(self.end)
        for col in cols[si:ei+1]:
            qt = df[col].quantile(self.percentile)
            if self.condition == 0:
                df = df.query(col + ' <= @qt')
            elif self.condition == 1:
                df = df.query(col + ' >= @qt')
        return df, kwargs

    def get_update_url(self):
        return reverse('collect:exclude_update', kwargs={'pk': self.id})

class PCAF(Process):
    ScalerChoices = ((0, 'None'), (1, 'MinMax'), (2, 'Standard'))
    scaler = models.PositiveSmallIntegerField(verbose_name='Scaler', choices=ScalerChoices, default=2)
    n_components = models.PositiveSmallIntegerField(verbose_name='N Components', default=8)
    start = models.CharField(verbose_name='Start column', max_length=50)
    end = models.CharField(verbose_name='End column', max_length=50)
    prefix = models.CharField(verbose_name='Prefix', max_length=100)
    replace = models.BooleanField(verbose_name='Replace', default=True)

    def process(self, df, **kwargs):
        feats = df.loc[:, self.start:self.end]
        nnan = feats.isnull().sum(axis=1)
        if nnan.sum() > 0:
            kwargs['{}_NaNError'.format(self.id)] = nnan
            return df, kwargs
        pipeline = []
        if self.scaler == 1:
            pipeline.append(('minmax', MinMaxScaler()))
        elif self.scaler == 2:
            pipeline.append(('standard', StandardScaler()))
        if self.n_components < len(feats.columns):
            pipeline.append(('pca', PCA(n_components=self.n_components)))
        else:
            pipeline.append(('pca', PCA()))
        model = Pipeline(pipeline)
        pca_feats = model.fit_transform(feats)
        ratio = model['pca'].explained_variance_ratio_
        kwargs['{}_Ratio'.format(self.id)] = ratio
        kwargs['{}_CumlativeRatio'.format(self.id)] = np.cumsum(ratio)
        columns = ['%s_PC%d' % (self.prefix, i + 1) for i in range(pca_feats.shape[1])]
        pcadf = pd.DataFrame(pca_feats, index=df.index, columns=columns)
        if self.replace:
            cols = list(df.columns)
            si = cols.index(self.start)
            ei = cols.index(self.end)
            df = df.drop(cols[si:ei+1], axis=1)
        return pd.concat([df, pcadf], axis=1), kwargs

    def get_update_url(self):
        return reverse('collect:pcaf_update', kwargs={'pk': self.id})

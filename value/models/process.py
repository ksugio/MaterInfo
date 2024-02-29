from config.settings import VALUE_FILTER_PROCESS
from django.utils.module_loading import import_string
from django.db import models
from django.urls import reverse
from project.models import Updated, Remote
from .value import Num2Alpha
from .filter import Filter
import pandas as pd
import numpy as np
import pybeads
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class Process(Updated, Remote):
    upper = models.ForeignKey(Filter, verbose_name='Filter', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Name', max_length=16, blank=True)
    order = models.SmallIntegerField(verbose_name='Order')

    def title(self):
        return '%s : %s_%d' % (self.upper.title, self.name, self.order)

    def get_detail_url(self):
        return reverse('value:filter_update', kwargs={'pk': self.upper.id})

    def get_update_url(self):
        pass

    def get_delete_url(self):
        return reverse('value:process_delete', kwargs={'pk': self.id})

    def get_table_url(self):
        return reverse('value:process_table', kwargs={'pk': self.id})

    def entity(self):
        if self.name:
            for item in VALUE_FILTER_PROCESS:
                if item['Model'].split('.')[-1] == self.name:
                    cls = import_string(item['Model'])
                    return cls.objects.get(id=self.id)
        else:
            for item in VALUE_FILTER_PROCESS:
                cls = import_string(item['Model'])
                obj = cls.objects.filter(id=self.id)
                if obj:
                    return obj[0]

    def process(self, df):
        return self.entity().process(df)

    def procval(self):
        df = self.upper.upper.read_csv()
        df = self.upper.procval(df, self.id)
        return df

class Select(Process):
    columns =  models.CharField(verbose_name='Columns', max_length=300)
    newnames =  models.CharField(verbose_name='New Names', max_length=300, blank=True, null=True)

    def process(self, df):
        ndf = pd.DataFrame([])
        if self.newnames:
            for col, name in zip(self.columns.split(','), self.newnames.split(',')):
                col = col.strip()
                if col in df.columns.values:
                    name = name.strip()
                    ndf[name] = df[col]
        else:
            for col in self.columns.split(','):
                col = col.strip()
                if col in df.columns.values:
                    ndf[col] = df[col]
        return ndf

    def get_update_url(self):
        return reverse('value:select_update', kwargs={'pk': self.id})

class Trim(Process):
    StartMethodChoices = ((0, 'First'), (1, 'Index'), (2, 'Larger'), (3, 'Smaller'), (4, 'Max'), (5, 'Min'))
    start_method = models.PositiveSmallIntegerField(verbose_name='Start method', choices=StartMethodChoices, default=0)
    start_index = models.PositiveIntegerField(verbose_name='Start index', blank=True, null=True)
    start_target =  models.CharField(verbose_name='Start target', max_length=50, blank=True, null=True)
    start_value = models.FloatField(verbose_name='Start value', blank=True, null=True)
    EndMethodChoices = ((0, 'Last'), (1, 'Index'), (2, 'Larger'), (3, 'Smaller'), (4, 'Max'), (5, 'Min'))
    end_method = models.PositiveSmallIntegerField(verbose_name='End method', choices=EndMethodChoices, default=0)
    end_index = models.PositiveIntegerField(verbose_name='End index', blank=True, null=True)
    end_target =  models.CharField(verbose_name='End target', max_length=50, blank=True, null=True)
    end_value = models.FloatField(verbose_name='End value', blank=True, null=True)
    DispChoices = ((0, 'Table'), (1, 'Plot'))
    disp = models.PositiveSmallIntegerField(verbose_name='Display', choices=DispChoices, default=0)

    def process(self, df):
        st = df.index[0]
        if self.start_method == 1 and self.start_index is not None:
            st = self.start_index
        elif self.start_method == 2 and self.start_target is not None:
            target = df[self.start_target]
            for i, value in target.items():
                if value >= self.start_value:
                    st = i
                    break
        elif self.start_method == 3 and self.start_target is not None:
            target = df[self.start_target]
            for i, value in target.items():
                if value <= self.start_value:
                    st = i
                    break
        elif self.start_method == 4 and self.start_target is not None:
            target = df[self.start_target]
            st = target.idxmax()
        elif self.start_method == 5 and self.start_target is not None:
            target = df[self.start_target]
            st = target.idxmin()
        ed = df.index[-1]
        if self.end_method == 1 and self.end_index is not None:
            ed = self.end_index
        elif self.end_method == 2 and self.end_target is not None :
            target = df[self.end_target][::-1]
            for i, value in target.items():
                if value >= self.end_value:
                    ed = i
                    break
        elif self.end_method == 3 and self.end_target is not None :
            target = df[self.end_target][::-1]
            for i, value in target.items():
                if value <= self.end_value:
                    ed = i
                    break
        elif self.end_method == 4 and self.end_target is not None :
            target = df[self.end_target]
            ed = target.idxmax()
        elif self.end_method == 5 and self.end_target is not None :
            target = df[self.end_target]
            ed = target.idxmin()
        return df.loc[st:ed]

    def plot(self):
        if self.start_target:
            df = self.procval()
            target = df[self.start_target]
            x = target.index
            y = target.values
            plt.plot(x, y)
        if self.end_target:
            df = self.procval()
            target = df[self.end_target]
            x = target.index
            y = target.values
            plt.plot(x, y)

    def get_update_url(self):
        return reverse('value:trim_update', kwargs={'pk': self.id})

class Operate(Process):
    MethodChoices = ((0, 'AddConst'), (1, 'SubConst'), (2, 'MultiConst'), (3, 'DivConst'), (4, 'PowConst'), (5, 'ModConst'),
                     (6, 'AddColumn'), (7, 'SubColumn'), (8, 'MultiColumn'), (9, 'DivColumn'), (10, 'PowColumn'), (11, 'ModColumn'),
                     (12, 'Exp'), (13, 'Log'), (14, 'Log2'), (15, 'Log10'), (16, 'Log1p'),
                     (17, 'Sin'), (18, 'Cos'), (19, 'Tan'), (20, 'ArcSin'), (21, 'ArcCos'), (22, 'ArcTan'),
                     (23, 'Sqrt'), (24, 'Abs'), (25, 'Round'), (26, 'Floor'), (27, 'Ceil'))
    method = models.PositiveSmallIntegerField(verbose_name='Method', choices=MethodChoices, default=0)
    targetcolumn = models.CharField(verbose_name='Target Column', max_length=50, blank=True, null=True)
    useindex = models.BooleanField(verbose_name='Use Index', default=False)
    const = models.FloatField(verbose_name='Const', blank=True, null=True)
    column = models.CharField(verbose_name='Column', max_length=50, blank=True, null=True)
    newname = models.CharField(verbose_name='New Name', max_length=50, blank=True, null=True)
    replace = models.BooleanField(verbose_name='Replace', default=False)
    DispChoices = ((0, 'Table'), (1, 'Plot'))
    disp = models.PositiveSmallIntegerField(verbose_name='Display', choices=DispChoices, default=0)

    def process(self, df):
        if self.targetcolumn in df.columns or self.useindex:
            if self.useindex:
                col1 = pd.Series(df.index.values)
            else:
                col1 = df[self.targetcolumn]
            if self.column is not None and self.column in df.columns:
                col2 = df[self.column]
            else:
                col2 = None
            if self.method == 0 and self.const is not None:
                col1 = col1 + self.const
            elif self.method == 1 and self.const is not None:
                col1 = col1 - self.const
            elif self.method == 2 and self.const is not None:
                col1 = col1 * self.const
            elif self.method == 3 and self.const is not None:
                col1 = col1 / self.const
            elif self.method == 4 and self.const is not None:
                col1 = col1.pow(self.const)
            elif self.method == 5 and self.const is not None:
                col1 = col1.mod(self.const)
            elif self.method == 6 and col2 is not None:
                col1 = col1 + col2
            elif self.method == 7 and col2 is not None:
                col1 = col1 - col2
            elif self.method == 8 and col2 is not None:
                col1 = col1 * col2
            elif self.method == 9 and col2 is not None:
                col1 = col1 / col2
            elif self.method == 10 and col2 is not None:
                col1 = col1.pow(col2)
            elif self.method == 11 and col2 is not None:
                col1 = col1.mod(col2)
            elif self.method == 12:
                col1 = np.exp(col1)
            elif self.method == 13:
                col1 = np.log(col1)
            elif self.method == 14:
                col1 = np.log2(col1)
            elif self.method == 15:
                col1 = np.log10(col1)
            elif self.method == 16:
                col1 = np.log1p(col1)
            elif self.method == 17:
                col1 = np.sin(col1)
            elif self.method == 18:
                col1 = np.cos(col1)
            elif self.method == 19:
                col1 = np.tan(col1)
            elif self.method == 20:
                col1 = np.arcsin(col1)
            elif self.method == 21:
                col1 = np.arccos(col1)
            elif self.method == 22:
                col1 = np.arctan(col1)
            elif self.method == 23:
                col1 = np.sqrt(col1)
            elif self.method == 24:
                col1 = np.absolute(col1)
            elif self.method == 25:
                col1 = np.round(col1)
            elif self.method == 26:
                col1 = np.floor(col1)
            elif self.method == 27:
                col1 = np.ceil(col1)
            if self.replace:
                cn = self.targetcolumn
            else:
                if self.newname:
                    cn = self.newname
                else:
                    cn = Num2Alpha(df.shape[1]+1)
            df[cn] = col1
        return df

    def plot(self):
        df = self.procval()
        if self.replace:
            cn = self.targetcolumn
        else:
            if self.newname:
                cn = self.newname
            else:
                cn = df.columns.values[-1]
        y = df[cn].values
        x = np.arange(len(y))
        plt.plot(x, y)

    def get_update_url(self):
        return reverse('value:operate_update', kwargs={'pk': self.id})

class Rolling(Process):
    MethodChoices = ((0, 'Mean'), (1, 'Sum'))
    method = models.PositiveSmallIntegerField(verbose_name='Method', choices=MethodChoices, default=0)
    window = models.PositiveSmallIntegerField(verbose_name='Window')
    targetcolumn = models.CharField(verbose_name='Target column', max_length=50)
    center = models.BooleanField(verbose_name='Center', default=False)
    newname = models.CharField(verbose_name='New Name', max_length=50, blank=True, null=True)
    replace = models.BooleanField(verbose_name='Replace', default=False)
    DispChoices = ((0, 'Table'), (1, 'Plot'))
    disp = models.PositiveSmallIntegerField(verbose_name='Display', choices=DispChoices, default=0)

    def process(self, df):
        if self.targetcolumn in df.columns:
            col = df[self.targetcolumn]
            if self.method == 0:
               col = col.rolling(self.window, center=self.center, min_periods=1).mean()
            elif self.method == 1:
               col = col.rolling(self.window, center=self.center, min_periods=1).sum()
            if self.replace:
                cn = self.targetcolumn
            else:
                if self.newname:
                    cn = self.newname
                else:
                    cn = Num2Alpha(df.shape[1]+1)
            df[cn] = col
            return df

    def plot(self):
        df = self.procval()
        if self.replace:
            cn = self.targetcolumn
        else:
            if self.newname:
                cn = self.newname
            else:
                cn = df.columns.values[-1]
        y = df[cn].values
        x = np.arange(len(y))
        plt.plot(x, y)

    def get_update_url(self):
        return reverse('value:rolling_update', kwargs={'pk': self.id})

class Reduce(Process):
    step = models.PositiveSmallIntegerField(verbose_name='Step')

    def process(self, df):
        return df[::self.step]

    def get_update_url(self):
        return reverse('value:reduce_update', kwargs={'pk': self.id})

class Gradient(Process):
    x_target = models.CharField(verbose_name='X target', max_length=50)
    y_target = models.CharField(verbose_name='Y target', max_length=50)
    newname = models.CharField(verbose_name='New Name', max_length=50, blank=True, null=True)
    DispChoices = ((0, 'Table'), (1, 'Plot'))
    disp = models.PositiveSmallIntegerField(verbose_name='Display', choices=DispChoices, default=0)

    def process(self, df):
        xcol = df[self.x_target].values
        ycol = df[self.y_target].values
        dcol = np.gradient(ycol, xcol)
        if self.newname:
            cn = self.newname
        else:
            cn = Num2Alpha(df.shape[1]+1)
        df[cn] = dcol
        return df

    def plot(self):
        df = self.procval()
        if self.newname:
            cn = self.newname
        else:
            cn = df.columns.values[-1]
        y = df[cn].values
        x = df[self.x_target].values
        plt.plot(x, y)

    def get_update_url(self):
        return reverse('value:gradient_update', kwargs={'pk': self.id})

class Drop(Process):
    columns =  models.CharField(verbose_name='Columns', max_length=300)

    def process(self, df):
        for col in self.columns.split(','):
            col = col.strip()
            if col in df.columns.values:
                df = df.drop(columns=col)
        return df

    def get_update_url(self):
        return reverse('value:drop_update', kwargs={'pk': self.id})

class Query(Process):
    condition = models.TextField(verbose_name='Condition')

    def process(self, df):
        try:
            return df.query(self.condition)
        except:
            return df

    def get_update_url(self):
        return reverse('value:query_update', kwargs={'pk': self.id})

class Eval(Process):
    expr = models.TextField(verbose_name='Expression')
    newname = models.CharField(verbose_name='New Name', max_length=50, blank=True, null=True)

    def process(self, df):
        try:
            col = df.eval(self.expr)
            if self.newname:
                cn = self.newname
            else:
                cn = Num2Alpha(df.shape[1] + 1)
            df[cn] = col
            return df
        except:
            return df

    def get_update_url(self):
        return reverse('value:eval_update', kwargs={'pk': self.id})

class Beads(Process):
    targetcolumn = models.CharField(verbose_name='Target column', max_length=50)
    newname = models.CharField(verbose_name='New name', max_length=50)
    withbg = models.BooleanField(verbose_name='With background', default=False)
    leftext = models.PositiveSmallIntegerField(verbose_name='Left extend', default=500)
    rightext = models.PositiveSmallIntegerField(verbose_name='Right extend', default=500)
    fc = models.FloatField(verbose_name='Cutoff frequency', default=0.006)
    amp = models.FloatField(verbose_name='Amplitude', default=0.8)
    DispChoices = ((0, 'Table'), (1, 'Plot'))
    disp = models.PositiveSmallIntegerField(verbose_name='Display', choices=DispChoices, default=0)

    def process(self, df):
        y = df[self.targetcolumn].values
        lexty = y[0] * self.sigmoid(np.arange(-5, 5, 10 / self.leftext))
        rexty = y[-1] * self.sigmoid(-np.arange(-5, 5, 10 / self.rightext))
        y = np.hstack([lexty, y, rexty])
        fc = self.fc
        d = 1
        r = 6
        amp = self.amp
        lam0 = 0.5 * amp
        lam1 = 5 * amp
        lam2 = 4 * amp
        Nit = 15
        pen = 'L1_v2'
        signal_est, bg_est, cost = pybeads.beads(y, d, fc, r, Nit, lam0, lam1, lam2, pen, conv=None)
        df[self.newname] = signal_est[self.leftext:-self.rightext]
        if self.withbg:
            df[self.newname+'_Bg'] = bg_est[self.leftext:-self.rightext]
        return df

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    def plot(self):
        df = self.procval()
        y = df[self.newname].values
        x = np.arange(len(y))
        plt.plot(x, y)

    def get_update_url(self):
        return reverse('value:beads_update', kwargs={'pk': self.id})
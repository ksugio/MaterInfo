from django.db import models
from django.utils.module_loading import import_string
from project.models import Project, Created, Updated, Remote, ModelUploadTo, PrefixPtr, Prefix
from django.urls import reverse
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from io import BytesIO
import pandas as pd
import json
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class Design(Created, Updated, Remote, PrefixPtr):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Valid'), (1, 'Invalid'), (2, 'Pending'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    ngen = models.PositiveIntegerField(verbose_name='Number of generates', default=100000)
    modelfunc = models.TextField(verbose_name='Model Function', blank=True)
    columns = models.TextField(verbose_name='Columns', blank=True)
    file = models.FileField(verbose_name='File', upload_to=ModelUploadTo, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('design:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('design:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('design:update', kwargs={'pk': self.id})

    def get_editnote_url(self):
        return reverse('design:edit_note', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('design:delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('design:api_update', kwargs={'pk': self.id})

    def get_candidates(self):
        cls = import_string('design.models.condition.Condition')
        condition = cls.objects.filter(upper=self)
        columns = {}
        for con in condition:
            columns[con.prefix] = con.prefix_display()
        if columns:
            self.columns = json.dumps(columns)
        cand = {}
        for cond in condition:
            cand[cond.prefix] = cond.candidates(self.ngen)
        if cand:
            df = pd.DataFrame(cand).drop_duplicates()
            self.save_csv(df)

    def save_csv(self, df):
        buf = BytesIO()
        df.to_csv(buf, index=False, mode="wb", encoding='UTF-8')
        self.file.save('Design.csv', buf, save=False)
        buf.close()

    def read_csv(self):
        if self.file:
            with self.file.open('r') as f:
                return pd.read_csv(f)
        return None

    def random_candidate(self):
        df = self.read_csv()
        if df is not None:
            columns = json.loads(self.columns)
            df.columns = [columns[col] for col in df.columns]
            ran = random.randint(1, df.shape[0])
            return df.iloc[ran - 1].to_dict()

    def get_experiments(self):
        cls = import_string('design.models.experiment.Experiment')
        experiment = cls.objects.filter(upper=self)
        exper = []
        props = []
        for ex in experiment:
            if ex.condition:
                exper.append(json.loads(ex.condition))
                props.append(ex.property)
        if exper and self.columns:
            edf = pd.DataFrame(exper)
            columns = list(json.loads(self.columns).keys())
            for col in edf.columns:
                if col not in columns:
                    edf.pop(col)
            edf['Property'] = props
            return edf

    def prefix_updated(self):
        prefix = Prefix.objects.filter(unique=self.prefix)
        if prefix:
            if prefix[0].updated_at > self.updated_at:
                return True
        if self.columns:
            columns = json.loads(self.columns)
            for key in columns.keys():
                prefix = Prefix.objects.filter(unique=key)
                if prefix:
                    if prefix[0].updated_at > self.updated_at:
                        return True
        return False

    def disp_table(self, **kwargs):
        df = self.read_csv()
        if df is not None:
            columns = json.loads(self.columns)
            df.columns = [columns[col] for col in df.columns]
        return df

    def plot(self, **kwargs):
        edf = self.get_experiments()
        if edf is None:
            return
        edf = edf.dropna()
        if edf.shape[0] <= 1:
            return
        props = edf.pop('Property').values
        mmscaled = MinMaxScaler().fit_transform(edf.values)
        pca = PCA(n_components=2)
        transformed = pca.fit_transform(mmscaled)
        pdf = pd.DataFrame(transformed, index=edf.index)
        fig, ax = plt.subplots()
        sc = ax.scatter(pdf[0], pdf[1], marker='o', c=props, cmap='viridis')
        fig.colorbar(sc)
        for ind in pdf.index:
            ax.text(pdf.loc[ind, 0], pdf.loc[ind, 1], ind)
        plt.xlabel('PC1')
        plt.ylabel('PC2')


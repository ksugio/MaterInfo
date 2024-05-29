from django import forms
from project.forms import ClearableFileInput
from .models.collect import Collect
from .models.process import Fillna, Drop, Select, Exclude, PCAF
from .models.reduction import Reduction, ReductionModel
from .models.clustering import Clustering, ClusteringModel
from .models.classification import Classification
from .models.classification_lib import ClassificationModel
from .models.regression import Regression
from .models.regression_lib import HParam2Dict, RegressionModel
from .models.inverse import Inverse

class CollectAddForm(forms.ModelForm):
    method = forms.ChoiceField(label='Method', choices=((0, 'Collect'), (1, 'Upload'), (2, 'Get')), initial=0)
    uploadfile = forms.fields.FileField(label='File', required=False)
    url = forms.CharField(label='URL', max_length=256, required=False,
                          widget=forms.Textarea(attrs={'cols': '100', 'rows': '1'}))

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data['method']
        uploadfile = cleaned_data['uploadfile']
        url = cleaned_data['url']
        if method == '1' and not uploadfile:
            raise forms.ValidationError("File is required for upload method.")
        elif method == '2' and not url:
            raise forms.ValidationError("URL is required for get method.")

    class Meta:
        model = Collect
        fields = ('title', 'note', 'projectids', 'disp_head', 'disp_tail')


class CollectUpdateForm(forms.ModelForm):
    collect = forms.fields.BooleanField(label='Collect', required=False, initial=False)

    class Meta:
        model = Collect
        fields = ('title', 'status', 'note', 'projectids', 'disp_head', 'disp_tail')

class CollectLoadForm(forms.ModelForm):
    uploadfile = forms.fields.FileField(label='File', required=False)
    url = forms.CharField(label='URL', max_length=256, required=False,
                          widget=forms.Textarea(attrs={'cols': '100', 'rows': '1'}))

    class Meta:
        model = Collect
        fields = ('title', 'note')

class ReductionAddForm(forms.ModelForm):
    class Meta:
        model = Reduction
        fields = ('title', 'note', 'scaler', 'method', 'hparam',
                  'drop', 'label', 'colormap', 'colorbar', 'nplot')

    def clean(self):
        cleaned_data = super().clean()
        try:
            dparam = HParam2Dict(cleaned_data['hparam'])
            ReductionModel(dparam, cleaned_data['scaler'], cleaned_data['method'])
        except:
            raise forms.ValidationError("Invalid Hypterparameter")

class ReductionUpdateForm(forms.ModelForm):
    class Meta:
        model = Reduction
        fields = ('title', 'status', 'note', 'scaler', 'method', 'hparam',
                  'drop', 'label', 'colormap', 'colorbar', 'nplot')

    def clean(self):
        cleaned_data = super().clean()
        try:
            dparam = HParam2Dict(cleaned_data['hparam'])
            ReductionModel(dparam, cleaned_data['scaler'], cleaned_data['method'])
        except:
            raise forms.ValidationError("Invalid Hypterparameter")

class ClusteringAddForm(forms.ModelForm):
    optimize = forms.fields.BooleanField(label='Optimize Hyperparameter', required=False, initial=False)

    class Meta:
        model = Clustering
        fields = ('title', 'note', 'scaler', 'reduction', 'n_components',
                  'method', 'hparam', 'drop', 'colormap', 'ntrials', 'score', 'optimize')

    def clean(self):
        cleaned_data = super().clean()
        try:
            dparam = HParam2Dict(cleaned_data['hparam'])
            ClusteringModel(dparam, cleaned_data['method'])
        except:
            raise forms.ValidationError("Invalid Hypterparameter")

class ClusteringUpdateForm(forms.ModelForm):
    optimize = forms.fields.BooleanField(label='Optimize Hyperparameter', required=False, initial=False)

    class Meta:
        model = Clustering
        fields = ('title', 'status', 'note', 'scaler', 'reduction', 'n_components',
                  'method', 'hparam', 'drop', 'colormap', 'ntrials', 'score', 'optimize')

    def clean(self):
        cleaned_data = super().clean()
        try:
            dparam = HParam2Dict(cleaned_data['hparam'])
            ClusteringModel(dparam, cleaned_data['method'])
        except:
            raise forms.ValidationError("Invalid Hypterparameter")

class ClassificationAddForm(forms.ModelForm):
    objective = forms.fields.ChoiceField(label='Objective')
    optimize = forms.fields.BooleanField(label='Optimize Hyperparameter', required=False, initial=False)

    class Meta:
        model = Classification
        fields = ('title', 'note', 'scaler', 'pca', 'n_components', 'method', 'hparam',
                  'objective', 'drop', 'nsplits', 'random', 'nplot', 'ntrials', 'optimize')

    def clean(self):
        cleaned_data = super().clean()
        try:
            dparam = HParam2Dict(cleaned_data['hparam'])
            ClassificationModel(dparam, cleaned_data['scaler'], cleaned_data['pca'],
                                cleaned_data['n_components'], cleaned_data['method'])
        except:
            raise forms.ValidationError("Invalid Hypterparameter")

class ClassificationUpdateForm(forms.ModelForm):
    objective = forms.fields.ChoiceField(label='Objective')
    optimize = forms.fields.BooleanField(label='Optimize Hyperparameter', required=False, initial=False)

    class Meta:
        model = Classification
        fields = ('title', 'status', 'note', 'scaler', 'pca', 'n_components', 'method', 'hparam',
                  'objective', 'drop', 'nsplits', 'random', 'nplot', 'ntrials', 'optimize')

    def clean(self):
        cleaned_data = super().clean()
        try:
            dparam = HParam2Dict(cleaned_data['hparam'])
            ClassificationModel(dparam, cleaned_data['scaler'],  cleaned_data['pca'],
                                cleaned_data['n_components'], cleaned_data['method'])
        except:
            raise forms.ValidationError("Invalid Hypterparameter")

class RegressionAddForm(forms.ModelForm):
    objective = forms.fields.ChoiceField(label='Objective')
    optimize = forms.fields.BooleanField(label='Optimize Hyperparameter', required=False, initial=False)
    columns_text = ''

    class Meta:
        model = Regression
        fields = ('title', 'note', 'scaler', 'pca', 'n_components', 'method', 'hparam',
                  'objective', 'drop', 'nsplits', 'random', 'nplot', 'ntrials', 'optimize')

    def clean(self):
        cleaned_data = super().clean()
        try:
            dparam = HParam2Dict(cleaned_data['hparam'])
            RegressionModel(dparam, cleaned_data['scaler'], cleaned_data['pca'],
                            cleaned_data['n_components'], cleaned_data['method'])
        except:
            raise forms.ValidationError("Invalid Hypterparameter")
        ldrop = cleaned_data['drop'].replace('\n', '').replace('\r', '').replace(' ', '').split(',')
        columns = self.columns_text.split(',')
        for col in ldrop:
            if col:
                if col not in columns:
                    raise forms.ValidationError("Invalid drop name : " + col)

class RegressionUpdateForm(forms.ModelForm):
    objective = forms.fields.ChoiceField(label='Objective')
    optimize = forms.fields.BooleanField(label='Optimize Hyperparameter', required=False, initial=False)
    columns_text = ''

    class Meta:
        model = Regression
        fields = ('title', 'status', 'note', 'scaler', 'pca', 'n_components', 'method', 'hparam',
                  'objective', 'drop', 'nsplits', 'random', 'nplot', 'ntrials', 'optimize')

    def clean(self):
        cleaned_data = super().clean()
        try:
            dparam = HParam2Dict(cleaned_data['hparam'])
            RegressionModel(dparam, cleaned_data['scaler'], cleaned_data['pca'],
                            cleaned_data['n_components'], cleaned_data['method'])
        except:
            raise forms.ValidationError("Invalid Hypterparameter")
        ldrop = cleaned_data['drop'].replace('\n', '').replace('\r', '').replace(' ', '').split(',')
        columns = self.columns_text.split(',')
        for col in ldrop:
            if col:
                if col not in columns:
                    raise forms.ValidationError("Invalid drop name : " + col)

class InverseAddForm(forms.ModelForm):
    regression1 = forms.fields.ChoiceField(label='Regression 1')
    regression2 = forms.fields.ChoiceField(label='Regression 2', required=False)
    regression3 = forms.fields.ChoiceField(label='Regression 3', required=False)

    class Meta:
        model = Inverse
        fields = ('title', 'note', 'regression1', 'target1',
                  'regression2', 'target2', 'regression3', 'target3',
                  'ntrials', 'seed')

class InverseUpdateForm(forms.ModelForm):
    regression1 = forms.fields.ChoiceField(label='Regression 1')
    regression2 = forms.fields.ChoiceField(label='Regression 2', required=False)
    regression3 = forms.fields.ChoiceField(label='Regression 3', required=False)
    optimize = forms.fields.BooleanField(label='Optimize', required=False, initial=False)

    class Meta:
        model = Inverse
        fields = ('title', 'status', 'note', 'regression1', 'target1',
                  'regression2', 'target2', 'regression3', 'target3',
                  'ntrials', 'seed', 'optimize')

class FillnaForm(forms.ModelForm):
    start = forms.fields.ChoiceField(label='Start column')
    end = forms.fields.ChoiceField(label='End column')

    class Meta:
        model = Fillna
        fields = ('groupby', 'start', 'end', 'method', 'order')

class DropForm(forms.ModelForm):
    start = forms.fields.ChoiceField(label='Start column')
    end = forms.fields.ChoiceField(label='End column')

    class Meta:
        model = Drop
        fields = ('start', 'end', 'order')

class SelectForm(forms.ModelForm):
    multi = forms.MultipleChoiceField(label='Select columns', required=True,
                                      widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Select
        fields = ('method', 'multi', 'order')

class ExcludeForm(forms.ModelForm):
    start = forms.fields.ChoiceField(label='Start column')
    end = forms.fields.ChoiceField(label='End column')

    class Meta:
        model = Exclude
        fields = ('percentile', 'condition', 'start', 'end', 'order')

class PCAFForm(forms.ModelForm):
    start = forms.fields.ChoiceField(label='Start column')
    end = forms.fields.ChoiceField(label='End column')

    class Meta:
        model = PCAF
        fields = ('scaler', 'n_components', 'start', 'end', 'prefix', 'replace', 'order')

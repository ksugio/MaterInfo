from django import forms
from project.forms import ClearableFileInput
from .models.value import Value, CSVFile
from .models.aggregate import Aggregate
from .models.curve import Curve

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ValueAddForm(forms.Form):
    file = MultipleFileField(label='File')
    note = forms.CharField(label='Note', widget=forms.Textarea, required=False)
    delimiter = forms.ChoiceField(label='Delimiter', choices=CSVFile.DelimiterChoices, initial=0)
    encoding = forms.ChoiceField(label='Encoding', choices=CSVFile.EncodingChoices, initial=0)
    skiprows = forms.IntegerField(label='Skiprows', initial=0)
    skipends = forms.IntegerField(label='Skipends', initial=0)
    header = forms.BooleanField(label='Header', initial=False, required=False)
    startstring = forms.CharField(label='Start String', max_length=100, required=False)
    endstring = forms.CharField(label='End String', max_length=100, required=False)
    datatype = forms.ChoiceField(label='Data type', choices=Value.DataTypeChoices, initial=0)
    disp_head = forms.IntegerField(label='Display Head', initial=50)
    disp_tail = forms.IntegerField(label='Display Tail', initial=50)

class ValueUpdateForm(forms.ModelForm):
    class Meta:
        model = Value
        fields = ('title', 'status', 'note', 'file', 'delimiter', 'encoding', 'skiprows', 'skipends',
                  'header', 'startstring', 'endstring', 'datatype', 'disp_head', 'disp_tail')
        widgets = {
            'file': ClearableFileInput(),
        }

class GenerateForm(forms.Form):
    title = forms.CharField(label='Title', max_length=100)
    note = forms.CharField(label='Note', widget=forms.Textarea, required=False)
    TYPE_CHOICES = ((0, 'Range'), (1, 'Linear'),  (2, 'Uniform Random'), (3, 'Normal Random'))
    type = forms.ChoiceField(label='Type', choices=TYPE_CHOICES, initial=0)
    start = forms.FloatField(label='Start', initial=0)
    stop = forms.FloatField(label='Stop', initial=100)
    step = forms.FloatField(label='Step', initial=1)
    num = forms.IntegerField(label='Number', initial=100)
    low = forms.FloatField(label='Low', initial=0.0)
    high = forms.FloatField(label='High', initial=1.0)
    mean = forms.FloatField(label='Mean', initial=0.0)
    std = forms.FloatField(label='STD', initial=1.0)

class AggregateAddForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Aggregate
        fields = ('title', 'note', 'prefix', 'category', 'column')

class AggregateUpdateForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Aggregate
        fields = ('title', 'status', 'note', 'prefix', 'category', 'column')

class CurveAddForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Curve
        fields = ('title', 'note', 'prefix', 'category', 'template',
                  'columnx', 'columny', 'startid', 'endid')

class CurveUpdateForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Curve
        fields = ('title', 'status', 'note', 'prefix', 'category', 'template',
                  'columnx', 'columny', 'startid', 'endid')

from django import forms
from project.forms import ClearableFileInput
from .models.image import Image
from .models.size import Size
from .models.ln2d import LN2D
from .models.imfp import IMFP
from .models.voronoi import Voronoi
from .models.measure import Measure

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleImageField(forms.ImageField):
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

class ImageAddForm(forms.Form):
    file = MultipleImageField(label='Image')
    note = forms.CharField(label='Note', widget=forms.Textarea, required=False)
    scale = forms.FloatField(label='Scale', initial=1.0)
    scaleunit = forms.ChoiceField(label='Scale unit', choices=Image.UnitChoices, initial=0)
    scalepixels = forms.IntegerField(label='Scale pixels', initial=1)
    device = forms.ChoiceField(label='Device', choices=Image.DeviceChoices, initial=0)

class ImageUpdateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('title', 'status', 'note', 'file', 'scale', 'scaleunit', 'scalepixels', 'device')
        widgets = {
            'file': ClearableFileInput(),
        }

class ImageGetForm(forms.Form):
    url = forms.CharField(label='URL', max_length=256, required=True,
                          widget=forms.Textarea(attrs={'cols': '100', 'rows': '1'}))
    title = forms.CharField(label='Title', max_length=100)
    note = forms.CharField(label='Note', widget=forms.Textarea, required=False)
    scale = forms.FloatField(label='Scale', initial=1.0)
    scaleunit = forms.ChoiceField(label='Scale unit', choices=Image.UnitChoices, initial=0)
    scalepixels = forms.IntegerField(label='Scale pixels', initial=1)
    device = forms.ChoiceField(label='Device', choices=Image.DeviceChoices, initial=0)

class ContoursForm(forms.Form):
    gc = forms.BooleanField(label='Gravity Center', required=False)
    bb = forms.BooleanField(label='Bounding Box', required=False)

class SizeAddForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Size
        fields = ('title', 'note', 'prefix', 'mindia', 'roiarea')

class SizeUpdateForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Size
        fields = ('title', 'status', 'note', 'prefix', 'mindia', 'roiarea')

class SizePlotForm(forms.Form):
    bins = forms.IntegerField(label='Bins')

    def clean(self):
        cleaned_data = super().clean()
        bins = cleaned_data.get("bins")
        if bins <= 1:
            raise forms.ValidationError("Bins should be larger than 1")

class LN2DAddForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = LN2D
        fields = ('title', 'note', 'prefix', 'lnmax', 'ntrials', 'randseed')

class LN2DUpdateForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = LN2D
        fields = ('title', 'status', 'note', 'prefix', 'lnmax', 'ntrials', 'randseed')

class LN2DPlotForm(forms.Form):
    lnmax = forms.IntegerField(label='LNMax')
    uniform = forms.BooleanField(label='Uniform', required=False)

    def clean(self):
        cleaned_data = super().clean()
        lnmax = cleaned_data.get("lnmax")
        if lnmax <= 1:
            raise forms.ValidationError("LNMax should be larger than 1")

class IMFPAddForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = IMFP
        fields = ('title', 'note', 'prefix', 'barrier', 'nclass', 'ntrials', 'randseed')

class IMFPUpdateForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = IMFP
        fields = ('title', 'status', 'note', 'prefix', 'barrier', 'nclass', 'ntrials', 'randseed')

class IMFPPlotForm(forms.Form):
    nclass = forms.IntegerField(label='NClass')

    def clean(self):
        cleaned_data = super().clean()
        nclass = cleaned_data.get("nclass")
        if nclass <= 1:
            raise forms.ValidationError("NClass should be larger than 1")

class VoronoiAddForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Voronoi
        fields = ('title', 'note', 'prefix')

class VoronoiUpdateForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Voronoi
        fields = ('title', 'status', 'note', 'prefix')

class VoronoiPlotForm(forms.Form):
    bins = forms.IntegerField(label='Bins')

    def clean(self):
        cleaned_data = super().clean()
        bins = cleaned_data.get("bins")
        if bins <= 1:
            raise forms.ValidationError("Bins should be larger than 1")

class MeasureAddForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Measure
        fields = ('title', 'note', 'type', 'prefix')

class MeasureUpdateForm(forms.ModelForm):
    prefix = forms.fields.ChoiceField(label='Prefix')

    class Meta:
        model = Measure
        fields = ('title', 'status', 'note', 'prefix')

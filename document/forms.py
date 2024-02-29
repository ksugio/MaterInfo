from django import forms

class DocumentForm(forms.Form):
    file = forms.FileField(label='File', required=True)
    note = forms.CharField(label='Note', required=False, widget=forms.Textarea())
    comment = forms.CharField(label='Comment', required=False, widget=forms.Textarea(), initial='Initial upload')

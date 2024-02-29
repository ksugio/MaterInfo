from django import forms

class AddForm(forms.Form):
    title = forms.CharField(label='Title', max_length=100, required=True)
    titles = []

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data['title']
        if title in self.titles:
            raise forms.ValidationError("The title is already used.")
        if ' ' in title:
            raise forms.ValidationError("The title includes space.")

class CloneForm(forms.Form):
    url = forms.CharField(label='URL', max_length=100, required=True)
    branch = forms.CharField(label='Branch', max_length=100, required=False)
    newname = forms.CharField(label='New Name', max_length=100, required=False)
    titles = []

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data['url']
        if not url.endswith('.git'):
            raise forms.ValidationError("Invalid URL.")
        newname = cleaned_data['newname']
        if newname:
            title = newname
        else:
            title = url.split('/')[-1][:-4]
        if title in self.titles:
            raise forms.ValidationError("The title is already used.")
        if ' ' in title:
            raise forms.ValidationError("The title includes space.")

class NewBranchForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100, required=True)
    source = forms.ChoiceField(label='Source')
    names = []

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data['name']
        if name in self.names:
            raise forms.ValidationError("The name is already used.")
        if ' ' in name:
            raise forms.ValidationError("The name includes space.")

from django import forms
from .models.item import Item

class ItemForm(forms.ModelForm):
    url = forms.CharField(label='URL', max_length=256, required=True,
                          widget=forms.Textarea(attrs={'cols': '100', 'rows': '1'}))

    class Meta:
        model = Item
        fields = ('url', 'columnx', 'columny', 'type', 'color', 'edgecolor',
                  'linewidth', 'linestyle', 'marker', 'markersize', 'bins',
                  'label', 'order')

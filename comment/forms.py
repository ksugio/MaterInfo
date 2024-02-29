from django import forms
from .models import Comment, Response

class CommentForm(forms.ModelForm):
    sendemail = forms.BooleanField(label='Send Email', initial=True, required=False)

    class Meta:
        model = Comment
        fields = ('title', 'comment', 'file')

class ResponseForm(forms.ModelForm):
    sendemail = forms.BooleanField(label='Send Email', initial=True, required=False)

    class Meta:
        model = Response
        fields = ('response', 'file')

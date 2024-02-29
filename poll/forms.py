from django import forms
from project.forms import ClearableFileInput
from .models import Poll, Answer

class PollUpdateForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ('title', 'status', 'note', 'file')
        widgets = {
            'file': ClearableFileInput(),
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('answer',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['answer'].label = ''


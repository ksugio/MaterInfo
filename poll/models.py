from django.db import models
from project.models import Created, Updated, RemoteRoot, Remote, Project, ModelUploadTo
from django.urls import reverse
import os

def PollUploadTo(instance, filename):
    return filename

class Poll(Created, Updated, RemoteRoot):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Accepting'), (1, 'Finish'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    file = models.FileField(verbose_name='File', upload_to=ModelUploadTo, blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('poll:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('poll:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('poll:update', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('poll:api_update', kwargs={'pk': self.id})

    def basename(self):
        return os.path.basename(self.file.name)

class Question(Updated, Remote):
    upper = models.ForeignKey(Poll, verbose_name='Poll', on_delete=models.CASCADE)
    question = models.CharField(verbose_name='Question', max_length=100)
    order = models.SmallIntegerField(verbose_name='Order')

    def title(self):
        return '%s : %s' % (self.upper.title, self.question)

    def get_detail_url(self):
        return reverse('poll:update', kwargs={'pk': self.upper.id})

    def get_update_url(self):
        return reverse('poll:question_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('poll:question_delete', kwargs={'pk': self.id})

class Answer(Updated, Remote):
    upper = models.ForeignKey(Question, on_delete=models.CASCADE)
    AnswerChoices = ((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'))
    answer = models.PositiveSmallIntegerField(verbose_name='Answer', choices=AnswerChoices, default=0)

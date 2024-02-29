from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from accounts.models import CustomUser
from plot.models.item import ColorChoices
from project.models import Created, Updated, Remote, RemoteRoot, Project

def check_comp(value):
    if value < 0 or value > 100:
        raise ValidationError('Input value from 0 to 100.')

def check_step(value):
    if value <= 0:
        raise ValidationError('Input value larger than 0.')

class Schedule(Created, Updated, RemoteRoot):
    upper = models.ForeignKey(Project, verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    StatusChoices = ((0, 'Ongoing'), (1, 'Finish'), (2, 'Cancel'))
    status = models.PositiveSmallIntegerField(verbose_name='Status', choices=StatusChoices, default=0)
    note = models.TextField(verbose_name='Note', blank=True)
    XLabelChoices = ((0, 'Day'), (1, 'Week'), (2, 'Month'), (3, 'Year'))
    xlabel = models.PositiveSmallIntegerField(verbose_name='X Label', choices=XLabelChoices, default=1)
    xlabel_step = models.PositiveSmallIntegerField(verbose_name='X Label Step', default=1, validators=[check_step])
    color = models.PositiveSmallIntegerField(verbose_name='Color', choices=ColorChoices, default=0)
    tob = models.BooleanField(verbose_name='Top to Bottom', default=True)
    current = models.BooleanField(verbose_name='Show Current', default=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('schedule:list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('schedule:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('schedule:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('schedule:delete', kwargs={'pk': self.id})

class Plan(Created, Updated, Remote):
    upper = models.ForeignKey(Schedule, verbose_name='Schedule', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    start = models.DateField(verbose_name='Start')
    finish = models.DateField(verbose_name='Finish')
    complete = models.PositiveSmallIntegerField(verbose_name='Complete', default=0)
    person = models.ManyToManyField(CustomUser, verbose_name='Person', related_name='Schedule_person', blank=True)
    note = models.TextField(verbose_name='Note', blank=True)

    def get_detail_url(self):
        return reverse('schedule:update', kwargs={'pk': self.upper.id})

    def get_update_url(self):
        return reverse('schedule:plan_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('schedule:plan_delete', kwargs={'pk': self.id})
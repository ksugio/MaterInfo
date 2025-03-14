from django.urls import reverse
from django.http import HttpResponse
from config.settings import FONT_PATH
from project.views import base, base_api, remote
from project.models import Project
from project.forms import ImportForm, CloneForm, TokenForm, SetRemoteForm
from ..models import Calendar, Plan
from ..serializer import CalendarSerializer
from .plan import PlanRemote
from io import BytesIO
import calendar
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

class AddView(base.AddView):
    model = Calendar
    upper = Project
    fields = ('title', 'note')
    template_name ="project/default_add.html"

class ListView(base.ListView):
    model = Calendar
    upper = Project
    template_name = "project/default_list.html"
    navigation = [['Add', 'calendars:add'],
                  ['Import', 'calendars:import'],
                  ['Clone', 'calendars:clone']]

class DetailView(base.DetailView):
    model = Calendar
    template_name = "calendars/calendar_detail.html"

    def get_day_plans(self, day, plan):
        plans = []
        for p in plan:
            if p.start.astimezone().date() == day:
                plans.append(p)
        return plans

    def get_month_plans(self, current, upper):
        c = calendar.Calendar(firstweekday=6)
        mc = c.monthdatescalendar(current.year, current.month)
        plan = Plan.objects.filter(upper=upper).order_by('start')
        month_plans = []
        for week in mc:
            day_plans = []
            for day in week:
                plans = self.get_day_plans(day, plan)
                day_plans.append({'date':day, 'plans':plans})
            month_plans.append(day_plans)
        return month_plans

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        upper = self.model.objects.get(pk=self.kwargs['pk'])
        current = datetime.datetime(year=int(self.kwargs['year']),
                                    month=int(self.kwargs['month']),
                                    day=1)
        current = current.astimezone()
        if current.month == 1:
            previous = current.replace(year=current.year-1, month=12, day=1)
        else:
            previous = current.replace(month=current.month-1, day=1)
        if current.month == 12:
            next = current.replace(year=current.year+1, month=1, day=1)
        else:
            next = current.replace(month=current.month+1, day=1)
        context['today'] = datetime.date.today()
        context['current'] = current
        context['previous'] = previous
        context['next'] = next
        context['weeknames'] = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        context['monthplans'] = self.get_month_plans(current, upper)
        return context

class DayDetailView(base.DetailView):
    model = Calendar
    template_name = "calendars/calendar_day_detail.html"

    def get_day_plans(self, upper, current):
        plan = Plan.objects.filter(upper=upper).order_by('start')
        plans = []
        for p in plan:
            if p.start.astimezone().date() == current.date():
                plans.append(p)
        return plans

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        upper = self.model.objects.get(pk=self.kwargs['pk'])
        current = datetime.datetime(year=int(self.kwargs['year']),
                                    month=int(self.kwargs['month']),
                                    day=int(self.kwargs['day']))
        current = current.astimezone()
        previous = current - datetime.timedelta(days=1)
        next = current + datetime.timedelta(days=1)
        context['current'] = current
        context['previous'] = previous
        context['next'] = next
        context['dayplans'] = self.get_day_plans(upper, current)
        return context

class DayChartView(base.View):
    model = Calendar

    def get_day_plans(self, upper, current):
        plan = Plan.objects.filter(upper=upper).order_by('start')
        plans = []
        for p in plan:
            if p.start.astimezone().date() == current.date():
                plans.append(p)
        return plans

    def get_xticks(self, start_min, finish_max):
        if start_min.minute > 0:
            adjust = 60 - start_min.minute
        else:
            adjust = 0
        xticks = []
        i = 0
        while True:
            time = start_min + datetime.timedelta(hours=i, minutes=adjust)
            if time > finish_max:
                break
            else:
                xticks.append((time - start_min).seconds)
            i += 1
        return xticks

    def get_xticklabels(self, start_min, xticks):
        xticklabels = []
        for xtick in xticks:
            xticklabel = (start_min + datetime.timedelta(seconds=xtick)).strftime('%H')
            xticklabels.append(xticklabel)
        return xticklabels

    def get(self, request, **kwargs):
        upper = self.model.objects.get(pk=kwargs['pk'])
        current = datetime.datetime(year=int(kwargs['year']),
                                    month=int(kwargs['month']),
                                    day=int(kwargs['day']))
        current = current.astimezone()
        plans = self.get_day_plans(upper, current)
        if not plans:
            return HttpResponse('No Plans')
        fp = fm.FontProperties(fname=FONT_PATH)
        plt.figure()
        y = list(range(len(plans)))
        titles = []
        start_min = plans[0].start
        finish_max = plans[0].start
        for i in y:
            plan = plans[i]
            duration = (plan.finish - plan.start).seconds
            minutes2start = (plan.start - start_min).seconds
            if plan.finish > finish_max:
                finish_max = plan.finish
            plt.barh(y=i, width=duration, left=minutes2start, color='#1f77b4')
            titles.append(plan.title)
        plt.gca().invert_yaxis()
        plt.yticks(y, titles, fontproperties=fp)
        xticks = self.get_xticks(start_min, finish_max)
        plt.xticks(xticks, self.get_xticklabels(start_min.astimezone(), xticks))
        buf = BytesIO()
        plt.savefig(buf, format='svg', bbox_inches='tight')
        svg = buf.getvalue()
        buf.close()
        plt.close()
        return HttpResponse(svg, content_type='image/svg+xml')

class UpdateView(base.UpdateView):
    model = Calendar
    fields = ('title', 'status', 'note')
    template_name = "project/default_update.html"

class DeleteView(base.DeleteManagerView):
    model = Calendar
    template_name = "project/default_delete.html"

class EditNoteView(base.MDEditView):
    model = Calendar
    text_field = 'note'
    template_name = "project/default_mdedit.html"

class CalendarSearch(base.Search):
    model = Calendar

# API
class AddAPIView(base_api.AddAPIView):
    upper = Project
    serializer_class = CalendarSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Project
    model = Calendar
    serializer_class = CalendarSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Calendar
    serializer_class = CalendarSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Calendar
    serializer_class = CalendarSerializer

class CalendarRemote(remote.Remote):
    model = Calendar
    add_name = 'calendars:api_add'
    list_name = 'calendars:api_list'
    retrieve_name = 'calendars:api_retrieve'
    update_name = 'calendars:api_update'
    serializer_class = CalendarSerializer
    child_remote = [PlanRemote]

class ImportView(remote.ImportView):
    model = Calendar
    upper = Project
    form_class = ImportForm
    remote_class = CalendarRemote
    template_name = "project/default_import.html"
    title = 'Calendar Import'
    success_name = 'calendars:list'
    view_name = 'calendars:detail'
    view_args = 3

class CloneView(remote.CloneView):
    model = Calendar
    upper = Project
    form_class = CloneForm
    remote_class = CalendarRemote
    template_name = "project/default_clone.html"
    title = 'Calendar Clone'
    success_name = 'calendars:list'
    view_name = 'calendars:detail'
    view_args = 3

class TokenView(remote.TokenView):
    model = Calendar
    form_class = TokenForm
    success_names = ['calendars:pull', 'calendars:push']

class PullView(remote.PullView):
    model = Calendar
    remote_class = CalendarRemote
    success_name = 'calendars:detail'
    fail_name = 'calendars:token'

    def get_success_url(self):
        today = datetime.date.today()
        return reverse(self.success_name, kwargs={'pk': self.kwargs['pk'], 'year': today.year, 'month': today.month})

class PushView(remote.PushView):
    model = Calendar
    remote_class = CalendarRemote
    success_name = 'calendars:detail'
    fail_name = 'calendars:token'

    def get_success_url(self):
        today = datetime.date.today()
        return reverse(self.success_name, kwargs={'pk': self.kwargs['pk'], 'year': today.year, 'month': today.month})

class LogView(remote.LogView):
    model = Calendar

class SetRemoteView(remote.SetRemoteView):
    model = Calendar
    form_class = SetRemoteForm
    remote_class = CalendarRemote
    title = 'Calendar Set Remote'
    success_name = 'calendars:detail'
    view_name = 'calendars:detail'
    view_args = 3

    def get_success_url(self):
        today = datetime.date.today()
        return reverse(self.success_name, kwargs={'pk': self.kwargs['pk'], 'year': today.year, 'month': today.month})

class ClearRemoteView(remote.ClearRemoteView):
    model = Calendar
    remote_class = CalendarRemote
    success_name = 'calendars:detail'

    def get_success_url(self):
        today = datetime.date.today()
        return reverse(self.success_name, kwargs={'pk': self.kwargs['pk'], 'year': today.year, 'month': today.month})

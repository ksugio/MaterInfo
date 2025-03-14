from django.http import HttpResponse
from config.settings import FONT_PATH
from project.views import base, base_api, remote
from project.models import Project
from project.forms import ImportForm, CloneForm, TokenForm, SetRemoteForm
from ..models import Schedule, Plan
from ..serializer import ScheduleSerializer
from .plan import PlanRemote
from io import BytesIO
import datetime
from dateutil.relativedelta import relativedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

class AddView(base.AddView):
    model = Schedule
    upper = Project
    fields = ('title', 'note', 'xlabel', 'xlabel_step',
              'color', 'tob', 'current')
    template_name ="project/default_add.html"

class ListView(base.ListView):
    model = Schedule
    upper = Project
    template_name = "project/default_list.html"
    navigation = [['Add', 'schedule:add'],
                  ['Import', 'schedule:import'],
                  ['Clone', 'schedule:clone']]

class DetailView(base.DetailView):
    model = Schedule
    template_name = "schedule/schedule_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        plans = Plan.objects.filter(upper=model).order_by('start')
        if plans:
            context['no_plans'] = False
        else:
            context['no_plans'] = True
        return context

class UpdateView(base.UpdateView):
    model = Schedule
    fields = ('title', 'status', 'note', 'xlabel', 'xlabel_step',
              'color', 'tob', 'current')
    template_name = "schedule/schedule_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        context['plans'] = Plan.objects.filter(upper=model).order_by('start')
        return context

class DeleteView(base.DeleteManagerView):
    model = Schedule
    template_name = "project/default_delete.html"

class ChartView(base.View):
    model = Schedule

    def get_xticks(self, start_min, finish_max, month=True):
        xticks = []
        i = 0
        while True:
            if month:
                date = start_min + relativedelta(months=i)
            else:
                date = start_min + relativedelta(years=i)
            if date >= finish_max:
                break
            else:
                xticks.append((date - start_min).days)
            i += 1
        return xticks

    def get_xticklabels(self, start_min, xticks, fmt):
        xticklabels = []
        for xtick in xticks:
            xticklabel = (start_min + datetime.timedelta(days=xtick)).strftime(fmt)
            xticklabels.append(xticklabel)
        return xticklabels

    def get(self, request, **kwargs):
        schedule = self.model.objects.get(pk=kwargs['pk'])
        tasks = Plan.objects.filter(upper=schedule).order_by('start')
        if not tasks:
            return HttpResponse('No Plans')
        fp = fm.FontProperties(fname=FONT_PATH)
        plt.figure()
        y = range(len(tasks))
        titles = []
        start_min = tasks[0].start
        finish_max = tasks[0].start
        for i in y:
            task = tasks[i]
            duration = (task.finish - task.start).days
            days2start = (task.start - start_min).days
            if task.finish > finish_max:
                finish_max = task.finish
            alpha = 0.9 * task.complete / 100 + 0.1
            plt.barh(y=i, width=duration, left=days2start, alpha=alpha, color=schedule.get_color_display())
            names = ''
            for person in task.person.all():
                names = names + person.username + ','
            if len(names) > 0:
                title = '%s:%s' % (task.title, names.rstrip(','))
            else:
                title = task.title
            titles.append(title)
        if schedule.tob:
            plt.gca().invert_yaxis()
        plt.yticks(y, titles, fontproperties=fp)
        if schedule.xlabel == 0:
            xticks = list(range((finish_max - start_min).days + 1))[::schedule.xlabel_step]
            plt.xticks(xticks, self.get_xticklabels(start_min, xticks, '%m/%d'))
        elif schedule.xlabel == 1:
            xticks = list(range(0, (finish_max - start_min).days + 1, 7))[::schedule.xlabel_step]
            plt.xticks(xticks, self.get_xticklabels(start_min, xticks, '%b %d'))
        elif schedule.xlabel == 2:
            xticks = self.get_xticks(start_min, finish_max, True)[::schedule.xlabel_step]
            plt.xticks(xticks, self.get_xticklabels(start_min, xticks, '%b,%y'))
        elif schedule.xlabel == 3:
            xticks = self.get_xticks(start_min, finish_max, False)[::schedule.xlabel_step]
            plt.xticks(xticks, self.get_xticklabels(start_min, xticks, '%Y'))
        plt.title(schedule.title, fontproperties=fp)
        if schedule.current:
            curr = (datetime.date.today() - start_min).days
            if curr >= 0:
                plt.axvline(x=curr, color=schedule.get_color_display())
        buf = BytesIO()
        plt.savefig(buf, format='svg', bbox_inches='tight')
        svg = buf.getvalue()
        buf.close()
        plt.close()
        return HttpResponse(svg, content_type='image/svg+xml')

class ScheduleSearch(base.Search):
    model = Schedule

# API
class AddAPIView(base_api.AddAPIView):
    upper = Project
    serializer_class = ScheduleSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Project
    model = Schedule
    serializer_class = ScheduleSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Schedule
    serializer_class = ScheduleSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Schedule
    serializer_class = ScheduleSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Schedule
    serializer_class = ScheduleSerializer

class ScheduleRemote(remote.Remote):
    model = Schedule
    add_name = 'schedule:api_add'
    list_name = 'schedule:api_list'
    retrieve_name = 'schedule:api_retrieve'
    update_name = 'schedule:api_update'
    delete_name = 'schedule:api_delete'
    serializer_class = ScheduleSerializer
    child_remote = [PlanRemote]

class ImportView(remote.ImportView):
    model = Schedule
    upper = Project
    form_class = ImportForm
    remote_class = ScheduleRemote
    template_name = "project/default_import.html"
    title = 'Schedule Import'
    success_name = 'schedule:list'
    view_name = 'schedule:detail'

class CloneView(remote.CloneView):
    model = Schedule
    form_class = CloneForm
    upper = Project
    remote_class = ScheduleRemote
    template_name = "project/default_clone.html"
    title = 'Schedule Clone'
    success_name = 'schedule:list'
    view_name = 'schedule:detail'

class TokenView(remote.TokenView):
    model = Schedule
    form_class = TokenForm
    success_names = ['schedule:pull', 'schedule:push']

class PullView(remote.PullView):
    model = Schedule
    remote_class = ScheduleRemote
    success_name = 'schedule:detail'
    fail_name = 'schedule:token'

class PushView(remote.PushView):
    model = Schedule
    remote_class = ScheduleRemote
    success_name = 'schedule:detail'
    fail_name = 'schedule:token'

class LogView(remote.LogView):
    model = Schedule

class SetRemoteView(remote.SetRemoteView):
    model = Schedule
    form_class = SetRemoteForm
    remote_class = ScheduleRemote
    title = 'Schedule Set Remote'
    success_name = 'schedule:detail'
    view_name = 'schedule:detail'

class ClearRemoteView(remote.ClearRemoteView):
    model = Schedule
    remote_class = ScheduleRemote
    success_name = 'schedule:detail'

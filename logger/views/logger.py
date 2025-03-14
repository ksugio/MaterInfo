from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from project.views import base, base_api, remote
from project.models import Project
from project.forms import ImportForm
from sample.models import Sample
from value.models.value import Value
from ..models import Logger
from ..forms import LoggerAddForm, LoggerUpdateForm, LoggerGrabForm
from ..serializer import LoggerSerializer
from io import StringIO, BytesIO
import redis
import time
import pandas as pd
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def GetData(model, period, elapsed=False):
    try:
        param = {
            'host': model.host,
            'port': model.port,
            'db': model.database
        }
        if model.password:
            param['password'] = model.password
        rd = redis.Redis(**param)
        print(rd)
        data_key = rd.get('data_key').decode()
        data_columns = rd.get('data_columns').decode().split(',')
        limit = int((time.time() - period) * 1000)
        lines = []
        times = []
        for item, score in rd.zrangebyscore(data_key, limit, float('inf'), withscores=True):
            lines.append(item.decode()[1:-1])
            times.append(datetime.datetime.fromtimestamp(score/1000))
        buf = StringIO('\n'.join(lines))
        df = pd.read_csv(buf, header=None)
        buf.close()
        df.columns = data_columns
        if elapsed:
            etimes = []
            for tm in times:
                etimes.append((tm - times[0]).total_seconds())
            df.insert(0, 'Elapsed Time', etimes)
        else:
            df.insert(0, 'DateTime', times)
        return df.drop(df.columns[-1], axis=1)
    except:
        return None

class AddView(base.AddView):
    model = Logger
    upper = Project
    form_class = LoggerAddForm
    template_name ="project/default_add.html"

    def test_func(self):
        upper = get_object_or_404(self.upper, id=self.kwargs['pk'])
        return self.request.user in base.ProjectMember(upper) and self.request.user.is_manager

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['title'].initial = 'Log' + base.DateToday()[2:]
        return form

class ListView(base.ListView):
    model = Logger
    upper = Project
    template_name = "project/default_list.html"
    navigation = [['Add', 'logger:add']]

class DetailView(base.DetailView):
    model = Logger
    template_name = "logger/logger_detail.html"
    navigation = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class UpdateView(base.UpdateView, base.FileSearch):
    model = Logger
    form_class = LoggerUpdateForm
    template_name = "project/default_update.html"

    def test_func(self):
        model = get_object_or_404(self.model, id=self.kwargs['pk'])
        return self.request.user in base.ProjectMember(model) and self.request.user.is_manager

class EditNoteView(base.MDEditView):
    model = Logger
    text_field = 'note'
    template_name = "project/default_mdedit.html"

    def test_func(self):
        model = get_object_or_404(self.model, id=self.kwargs['pk'])
        return self.request.user in base.ProjectMember(model) and self.request.user.is_manager

class DeleteView(base.DeleteView):
    model = Logger
    template_name = "project/default_delete.html"

    def test_func(self):
        model = get_object_or_404(self.model, id=self.kwargs['pk'])
        return self.request.user in base.ProjectMember(model) and self.request.user.is_manager

class MonitorView(base.View):
    model = Logger

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        return HttpResponse(self.plot_frame(model, self.kwargs['period']),
                           content_type='image/jpeg')
        # return StreamingHttpResponse(self.plot_gen(model, self.kwargs['period']),
        #                              content_type="multipart/x-mixed-replace;boundary=frame")

    def plot_frame(self, model, period):
        df = GetData(model, period)
        if df is None:
            return None
        nrow = len(df.columns.values[1:])
        plt.figure(figsize=(12, nrow * 3))
        for i, col in enumerate(df.columns.values[1:]):
            plt.subplot(nrow, 1, i+1)
            plt.plot(df['DateTime'], df[col])
            plt.ylabel(col)
        buf = BytesIO()
        plt.savefig(buf, format='jpeg', bbox_inches='tight')
        frame = buf.getvalue()
        buf.close()
        plt.close()
        return frame

    def plot_gen(self, model, period):
        while True:
            frame = self.plot_frame(model, period)
            if frame is None:
                break
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            time.sleep(model.interval)

def SampleCandidate(upper):
    samples = Sample.objects.filter(upper=upper)
    candidate = []
    for sample in samples:
        candidate.append((sample.id, sample.title))
    return candidate

class GrabView(base.FormView):
    model = Logger
    form_class = LoggerGrabForm
    template_name = "project/default_add.html"
    title = 'Logger Grab'
    success_name = 'logger:detail'

    def get_form(self, form_class=None):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        form.fields['start'].initial = datetime.datetime.now()
        form.fields['sample'].choices = SampleCandidate(model.upper)
        return form

    def form_valid(self, form):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        sample = Sample.objects.get(id=form.cleaned_data['sample'])
        title = model.title + ' @ ' + form.cleaned_data['start'].strftime('%y-%m-%d %H:%M:%S')
        note = form.cleaned_data['note']
        df = GetData(model, form.cleaned_data['period'], elapsed=True)
        buf = BytesIO()
        df.to_csv(buf, index=False, mode="wb", encoding="UTF-8", date_format="%y/%m/%d %H:%M:%S")
        file = InMemoryUploadedFile(ContentFile(buf.getvalue()), None, 'logger.csv', 'text/csv', None, None)
        buf.close()
        Value.objects.create(created_by=self.request.user, updated_by=self.request.user, upper=sample,
                             title=title, note=note, file=file, header=True)
        return super().form_valid(form)

class LoggerSearch(base.Search):
    model = Logger

# API
class AddAPIView(base_api.AddAPIView):
    permission_classes = (base_api.IsAuthenticated, base_api.IsMemberUp, base_api.IsManager)
    upper = Project
    serializer_class = LoggerSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Project
    model = Logger
    serializer_class = LoggerSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Logger
    serializer_class = LoggerSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    permission_classes = (base_api.IsAuthenticated, base_api.IsMemberUp, base_api.IsManager)
    model = Logger
    serializer_class = LoggerSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    permission_classes = (base_api.IsAuthenticated, base_api.IsMemberUp, base_api.IsManager)
    model = Logger
    serializer_class = LoggerSerializer

class LoggerRemote(remote.Remote):
    model = Logger
    add_name = 'logger:api_add'
    list_name = 'logger:api_list'
    retrieve_name = 'logger:api_retrieve'
    update_name = 'logger:api_update'
    delete_name = 'logger:api_delete'
    serializer_class = LoggerSerializer
    lower_remote = []

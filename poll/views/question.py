from django.http import HttpResponse
from project.views import base, base_api, remote
from project.forms import CSVFileForm
from ..models import Poll, Question
from ..serializer import QuestionSerializer
#from .answer import AnswerRemote
import datetime
import io
import csv

class AddView(base.AddView):
    model = Question
    upper = Poll
    fields = ('question', 'order')
    template_name ="project/default_add.html"
    bdcl_remove = 1

class UpdateView(base.UpdateView):
    model = Question
    fields = ('question', 'order')
    template_name = "project/default_update.html"
    bdcl_remove = 1

class DeleteView(base.DeleteView):
    model = Question
    template_name = "project/default_delete.html"
    bdcl_remove = 1

class UploadView(base.FormView):
    model = Question
    upper = Poll
    form_class = CSVFileForm
    template_name = "project/default_add.html"
    title = 'Question Upload'
    success_name = 'poll:update'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['btn_title'] = 'Upload'
        return context

    def form_valid(self, form):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        csvfile = io.TextIOWrapper(form.cleaned_data['csv_file'])
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            try:
                que = self.model.objects.get(pk=row[0], upper=upper)
                updated = False
                if que.question != row[1]:
                     que.question = row[1]
                     updated = True
                if que.order != int(row[2]):
                     que.order = row[2]
                     updated = True
                if updated:
                    que.save()
            except:
                self.model.objects.create(updated_by=self.request.user, upper=upper, question=row[1], order=row[2])
        return super().form_valid(form)

class DownloadView(base.View):
    upper = Poll

    def get(self, request, **kwargs):
        poll = self.upper.objects.get(pk=kwargs['pk'])
        response = HttpResponse(content_type='text/csv; charset=Shift-JIS')
        now = datetime.datetime.now()
        filename = 'Question%s.csv' % (now.strftime('%Y%m%d%H%M%S')[2:])
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
        writer = csv.writer(response)
        writer.writerow(['ID', 'Question', 'Order'])
        for que in Question.objects.filter(upper=poll).order_by('order'):
            writer.writerow([que.pk, que.question, que.order])
        return response

# API
class AddAPIView(base_api.AddAPIView):
    upper = Poll
    serializer_class = QuestionSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(updated_by=self.request.user, upper=upper)

class ListAPIView(base_api.ListAPIView):
    upper = Poll
    model = Question
    serializer_class = QuestionSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Question
    serializer_class = QuestionSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Question
    serializer_class = QuestionSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Question
    serializer_class = QuestionSerializer

class QuestionRemote(remote.Remote):
    model = Question
    add_name = 'poll:api_question_add'
    list_name = 'poll:api_question_list'
    retrieve_name = 'poll:api_question_retrieve'
    update_name = 'poll:api_question_update'
    delete_name = 'poll:api_question_delete'
    serializer_class = QuestionSerializer
    #child_remote = [AnswerRemote]
    synchronize = True

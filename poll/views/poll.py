from project.views import base, base_api, remote
from project.models import Project
from project.forms import EditNoteForm, ImportForm, CloneForm, TokenForm, SetRemoteForm
from ..models import Poll, Question, Answer
from ..forms import PollUpdateForm
from ..serializer import PollSerializer
from .question import QuestionRemote

class AddView(base.AddView):
    model = Poll
    upper = Project
    fields = ('title', 'note', 'file')
    template_name ="project/default_add.html"

class ListView(base.ListView):
    model = Poll
    upper = Project
    template_name = "project/default_list.html"
    navigation = [['Add', 'poll:add'],
                  ['Import', 'poll:import'],
                  ['Clone', 'poll:clone']]

class DetailView(base.DetailView):
    model = Poll
    template_name = "poll/poll_detail.html"
    navigation = [['Answer', 'poll:answer_add'],]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        if model.status > 0:
            context.pop('navigation_list')
        question = Question.objects.filter(upper=model).order_by('order')
        if len(question) == 0:
            context.pop('navigation_list')
        html = '<th>Username</th>'
        for item in question:
            ss = '<th>%s</th>' % (item.question)
            html = html + ss
        context['thead_html'] = html
        tbody_list = []
        total = [0] * len(question)
        nuser = 0
        for user in base.ProjectMember(model):
            html = '<td>%s</td>' % (user.username)
            c = 0
            for ques in question:
                ans = Answer.objects.filter(upper=ques, updated_by=user)
                if ans:
                    a = ans.get().answer
                    total[c] = total[c] + a
                    html = html + '<td>%d</td>' % (a)
                else:
                    html = html + '<td></td>'
                c = c + 1
            tbody_list.append(html)
        html = '<td><strong>Total</strong></td>'
        for t in total:
            html = html + '<td><strong>%d</strong></td>' % (t)
        tbody_list.append(html)
        context['tbody_list'] = tbody_list
        return context

class UpdateView(base.UpdateView):
    model = Poll
    form_class = PollUpdateForm
    template_name = "poll/poll_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        question = Question.objects.filter(upper=model).order_by('order')
        context['question'] = question
        return context

class EditNoteView(base.EditNoteView):
    model = Poll
    form_class = EditNoteForm
    template_name = "project/default_edit_note.html"

class FileView(base.FileView):
    model = Poll
    attachment = False

class PollSearch(base.Search):
    model = Poll

# API
class AddAPIView(base_api.AddAPIView):
    upper = Project
    serializer_class = PollSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Project
    model = Poll
    serializer_class = PollSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Poll
    serializer_class = PollSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Poll
    serializer_class = PollSerializer

class FileAPIView(base_api.FileAPIView):
    model = Poll
    attachment = False

class PollRemote(remote.FileRemote):
    model = Poll
    add_name = 'poll:api_add'
    list_name = 'poll:api_list'
    retrieve_name = 'poll:api_retrieve'
    update_name = 'poll:api_update'
    file_fields_names = [('file', 'poll:api_file')]
    serializer_class = PollSerializer
    child_remote = [QuestionRemote]

class ImportView(remote.ImportView):
    model = Poll
    upper = Project
    form_class = ImportForm
    remote_class = PollRemote
    template_name = "project/default_import.html"
    title = 'Poll Import'
    success_name = 'poll:list'
    view_name = 'poll:detail'

class CloneView(remote.CloneView):
    model = Poll
    form_class = CloneForm
    upper = Project
    remote_class = PollRemote
    template_name = "project/default_clone.html"
    title = 'Poll Clone'
    success_name = 'poll:list'
    view_name = 'poll:detail'

class TokenView(remote.TokenView):
    model = Poll
    form_class = TokenForm
    success_names = ['poll:pull', 'poll:push']

class PullView(remote.PullView):
    model = Poll
    remote_class = PollRemote
    success_name = 'poll:detail'
    fail_name = 'poll:token'

class PushView(remote.PushView):
    model = Poll
    remote_class = PollRemote
    success_name = 'poll:detail'
    fail_name = 'poll:token'

class SetRemoteView(remote.SetRemoteView):
    model = Poll
    form_class = SetRemoteForm
    remote_class = PollRemote
    title = 'Poll Set Remote'
    success_name = 'poll:detail'
    view_name = 'poll:detail'

class ClearRemoteView(remote.ClearRemoteView):
    model = Poll
    remote_class = PollRemote
    success_name = 'poll:detail'

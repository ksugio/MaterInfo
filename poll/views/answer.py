from django.shortcuts import render, redirect
from django.forms import formset_factory
from project.views import base, base_api, remote
from ..models import Poll, Question, Answer
from ..serializer import AnswerSerializer
from ..forms import AnswerForm

class AddView(base.View):
    template_name = "poll/answer_add.html"

    def test_func(self):
        poll = Poll.objects.get(pk=self.kwargs['pk'])
        return self.request.user in base.ProjectMember(poll)

    def getqanda(self, poll):
        question = Question.objects.filter(upper=poll).order_by('order')
        ans_list = []
        qid_list = []
        for ques in question:
            ans = Answer.objects.filter(upper=ques, updated_by=self.request.user)
            ans_list.append(ans)
            qid_list.append(ques.id)
        return question, ans_list, qid_list

    def get(self, request, **kwargs):
        poll = Poll.objects.get(pk=kwargs['pk'])
        if poll.status > 0:
            return redirect(poll.get_detail_url())
        question, ans_list, qid_list = self.getqanda(poll)
        AnswerFormSet = formset_factory(form=AnswerForm, extra=len(question))
        formset = AnswerFormSet()
        for form in formset:
            if len(ans_list) > 0:
                ans = ans_list.pop(0)
                if ans:
                    form.fields['answer'].initial = ans.get().answer
        params = {
            'formset': formset,
            'question': question,
            'poll': poll,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(poll)
        }
        return render(request, self.template_name, params)

    def post(self, request, **kwargs):
        poll = Poll.objects.get(pk=kwargs['pk'])
        question, ans_list, qid_list = self.getqanda(poll)
        AnswerFormSet = formset_factory(form=AnswerForm, extra=len(question))
        formset = AnswerFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                try:
                    val = form.cleaned_data['answer']
                except:
                    val = 0
                if len(ans_list) > 0:
                    ans = ans_list.pop(0)
                    if ans:
                        obj = ans.get()
                    else:
                        obj = Answer()
                else:
                    obj = Answer()
                obj.upper = question.get(id=qid_list.pop(0))
                obj.updated_by = request.user
                obj.answer = val
                obj.save()
            return redirect(poll.get_detail_url())
        else:
            params = {
                'formset': formset,
                'question': question,
                'poll': poll,
                'brand_name': self.brandName(),
                'breadcrumb_list': self.breadcrumbList(poll)
            }
            return render(request, self.template_name, params)

# API
class AddAPIView(base_api.AddAPIView):
    upper = Question
    serializer_class = AnswerSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(updated_by=self.request.user, upper=upper)

class ListAPIView(base_api.ListAPIView):
    upper = Question
    model = Answer
    serializer_class = AnswerSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Answer
    serializer_class = AnswerSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Answer
    serializer_class = AnswerSerializer

# class AnswerRemote(remote.Remote):
#     model = Answer
#     add_name = 'poll:api_answer_add'
#     list_name = 'poll:api_answer_list'
#     retrieve_name = 'poll:api_answer_retrieve'
#     update_name = 'poll:api_answer_update'
#     serializer_class = AnswerSerializer
#     synchronize = True
#     ignore_push = True
#
#     def updated_by(self, data, user, **kwargs):
#         if 'updated_by' in data and 'member' in kwargs:
#             for user in kwargs['member']:
#                 if user[0]['id'] == data['updated_by']:
#                     return user[1]
#         return None
#
#     def create(self, data, upper, user, **kwargs):
#         updated_by = self.updated_by(data, user, **kwargs)
#         if updated_by is not None:
#             option = {
#                 'upper': upper,
#                 'remoteid': data['id'],
#                 'remoteat': data['updated_at'],
#                 'updated_by': updated_by
#             }
#             serializer = self.serializer_class(data=data)
#             serializer.is_valid(raise_exception=True)
#             object = serializer.save(**option)
#             object.save(localupd=False)
#             return object, kwargs
#         else:
#             return None, kwargs
#
#     def update(self, model, data, user, **kwargs):
#         updated_by = self.updated_by(data, user, **kwargs)
#         if updated_by is not None:
#             option = {
#                 'remoteat': data['updated_at'],
#                 'updated_by': updated_by
#             }
#             serializer = self.serializer_class(model, data=data)
#             serializer.is_valid(raise_exception=True)
#             object = serializer.save(**option)
#             object.save(localupd=False)
#             return object, kwargs
#         else:
#             return None, kwargs

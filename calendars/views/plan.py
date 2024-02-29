from django.urls import reverse
from project.views import base, base_api, remote
from ..models import Calendar, Plan
from ..serializer import PlanSerializer
from ..forms import PlanForm
import datetime

class AddView(base.AddView):
    model = Plan
    upper = Calendar
    form_class = PlanForm
    template_name ="calendars/plan_add.html"
    bdcl_remove = 1

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        current = datetime.datetime(year=int(self.kwargs['year']),
                                    month=int(self.kwargs['month']),
                                    day=int(self.kwargs['day']))
        form.fields['start'].initial = current
        form.fields['finish'].initial = current
        return form

    def get_success_url(self):
        start = self.object.start.astimezone()
        kwargs = { 'pk': self.object.upper.id,
                   'year': start.year,
                   'month': start.month,
                   'day': start.day }
        return reverse('calendars:day_detail', kwargs=kwargs)

class UpdateView(base.UpdateView):
    model = Plan
    form_class = PlanForm
    template_name = "calendars/plan_update.html"
    bdcl_remove = 1

    def get_success_url(self):
        start = self.object.start.astimezone()
        kwargs = { 'pk': self.object.upper.id,
                   'year': start.year,
                   'month': start.month,
                   'day': start.day }
        return reverse('calendars:day_detail', kwargs=kwargs)

class DeleteView(base.DeleteView):
    model = Plan
    template_name = "calendars/plan_delete.html"
    bdcl_remove = 1

    def get_success_url(self):
        start = self.object.start.astimezone()
        kwargs = { 'pk': self.object.upper.id,
                   'year': start.year,
                   'month': start.month,
                   'day': start.day }
        return reverse('calendars:day_detail', kwargs=kwargs)

# API
class AddAPIView(base_api.AddAPIView):
    upper = Calendar
    serializer_class = PlanSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Calendar
    model = Plan
    serializer_class = PlanSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Plan
    serializer_class = PlanSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Plan
    serializer_class = PlanSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Plan
    serializer_class = PlanSerializer

class PlanRemote(remote.Remote):
    model = Plan
    add_name = 'calendars:api_plan_add'
    list_name = 'calendars:api_plan_list'
    retrieve_name = 'calendars:api_plan_retrieve'
    update_name = 'calendars:api_plan_update'
    delete_name = 'calendars:api_plan_delete'
    serializer_class = PlanSerializer
    synchronize = True

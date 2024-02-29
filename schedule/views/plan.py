from project.views import base, base_api, remote
from ..models import Schedule, Plan
from ..serializer import PlanSerializer
from ..forms import PlanForm

class AddView(base.AddView):
    model = Plan
    upper = Schedule
    form_class = PlanForm
    template_name ="schedule/plan_add.html"
    bdcl_remove = 1

class UpdateView(base.UpdateView):
    model = Plan
    form_class = PlanForm
    template_name = "schedule/plan_update.html"
    bdcl_remove = 1

class DeleteView(base.DeleteView):
    model = Plan
    template_name = "project/default_delete.html"
    bdcl_remove = 1

# API
class AddAPIView(base_api.AddAPIView):
    upper = Schedule
    serializer_class = PlanSerializer

class ListAPIView(base_api.ListAPIView):
    upper = Schedule
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
    add_name = 'schedule:api_plan_add'
    list_name = 'schedule:api_plan_list'
    retrieve_name = 'schedule:api_plan_retrieve'
    update_name = 'schedule:api_plan_update'
    delete_name = 'schedule:api_plan_delete'
    serializer_class = PlanSerializer
    synchronize = True


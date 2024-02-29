from django.utils.module_loading import import_string
from config.settings import VALUE_FILTER_PROCESS
from project.views import base_api, remote
from ..models.filter import Filter
from ..models import process
from .. import serializer

class AddAPIView(base_api.AddAPIView):
    upper = Filter
    serializer_class = None

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        name = self.serializer_class.Meta.model.__name__
        serializer.save(updated_by=self.request.user, upper=upper, name=name)

class ListAPIView(base_api.ListAPIView):
    upper = Filter
    model = process.Process
    serializer_class = serializer.ProcessSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = process.Process
    serializer_class = serializer.ProcessSerializer

class ProcessRemote(remote.SwitchRemote):
    model = process.Process
    add_name = None
    list_name = 'value:api_process_list'
    retrieve_name = None
    update_name = None
    delete_name = 'value:api_process_delete'
    serializer_class = serializer.ProcessSerializer
    synchronize = True
    upper_save = True

    def switcher(self, name):
        if name:
            for item in VALUE_FILTER_PROCESS:
                if item['Model'].split('.')[-1] == name and 'Remote' in item:
                    return import_string(item['Remote'])
        return None

    def data_switcher(self, data):
        return self.switcher(data['name'])

    def model_switcher(self, model):
        return self.switcher(model.name)

#
# Select
#
class SelectAddAPIView(AddAPIView):
    serializer_class = serializer.SelectSerializer

class SelectRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Select
    serializer_class = serializer.SelectSerializer

class SelectUpdateAPIView(base_api.UpdateAPIView):
    model = process.Select
    serializer_class = serializer.SelectSerializer

class SelectRemote(ProcessRemote):
    model = process.Select
    add_name = 'value:api_select_add'
    retrieve_name = 'value:api_select_retrieve'
    update_name = 'value:api_select_update'
    serializer_class = serializer.SelectSerializer

#
# Trim
#
class TrimAddAPIView(AddAPIView):
    serializer_class = serializer.TrimSerializer

class TrimRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Trim
    serializer_class = serializer.TrimSerializer

class TrimUpdateAPIView(base_api.UpdateAPIView):
    model = process.Trim
    serializer_class = serializer.TrimSerializer

class TrimRemote(ProcessRemote):
    model = process.Trim
    add_name = 'value:api_trim_add'
    retrieve_name = 'value:api_trim_retrieve'
    update_name = 'value:api_trim_update'
    serializer_class = serializer.TrimSerializer

#
# Operate
#
class OperateAddAPIView(AddAPIView):
    serializer_class = serializer.OperateSerializer

class OperateRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Operate
    serializer_class = serializer.OperateSerializer

class OperateUpdateAPIView(base_api.UpdateAPIView):
    model = process.Operate
    serializer_class = serializer.OperateSerializer

class OperateRemote(ProcessRemote):
    model = process.Operate
    add_name = 'value:api_operate_add'
    retrieve_name = 'value:api_operate_retrieve'
    update_name = 'value:api_operate_update'
    serializer_class = serializer.OperateSerializer

#
# Rolling
#
class RollingAddAPIView(AddAPIView):
    serializer_class = serializer.RollingSerializer

class RollingRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Rolling
    serializer_class = serializer.RollingSerializer

class RollingUpdateAPIView(base_api.UpdateAPIView):
    model = process.Rolling
    serializer_class = serializer.RollingSerializer

class RollingRemote(ProcessRemote):
    model = process.Rolling
    add_name = 'value:api_rolling_add'
    retrieve_name = 'value:api_rolling_retrieve'
    update_name = 'value:api_rolling_update'
    serializer_class = serializer.RollingSerializer

#
# Reduce
#
class ReduceAddAPIView(AddAPIView):
    serializer_class = serializer.ReduceSerializer

class ReduceRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Reduce
    serializer_class = serializer.ReduceSerializer

class ReduceUpdateAPIView(base_api.UpdateAPIView):
    model = process.Reduce
    serializer_class = serializer.ReduceSerializer

class ReduceRemote(ProcessRemote):
    model = process.Reduce
    add_name = 'value:api_reduce_add'
    retrieve_name = 'value:api_reduce_retrieve'
    update_name = 'value:api_reduce_update'
    serializer_class = serializer.ReduceSerializer

#
# Gradient
#
class GradientAddAPIView(AddAPIView):
    serializer_class = serializer.GradientSerializer

class GradientRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Gradient
    serializer_class = serializer.GradientSerializer

class GradientUpdateAPIView(base_api.UpdateAPIView):
    model = process.Gradient
    serializer_class = serializer.GradientSerializer

class GradientRemote(ProcessRemote):
    model = process.Gradient
    add_name = 'value:api_gradient_add'
    retrieve_name = 'value:api_gradient_retrieve'
    update_name = 'value:api_gradient_update'
    serializer_class = serializer.GradientSerializer

#
# Drop
#
class DropAddAPIView(AddAPIView):
    serializer_class = serializer.DropSerializer

class DropRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Drop
    serializer_class = serializer.DropSerializer

class DropUpdateAPIView(base_api.UpdateAPIView):
    model = process.Drop
    serializer_class = serializer.DropSerializer

class DropRemote(ProcessRemote):
    model = process.Drop
    add_name = 'value:api_drop_add'
    retrieve_name = 'value:api_drop_retrieve'
    update_name = 'value:api_drop_update'
    serializer_class = serializer.DropSerializer

#
# Query
#
class QueryAddAPIView(AddAPIView):
    serializer_class = serializer.QuerySerializer

class QueryRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Query
    serializer_class = serializer.QuerySerializer

class QueryUpdateAPIView(base_api.UpdateAPIView):
    model = process.Query
    serializer_class = serializer.QuerySerializer

class QueryRemote(ProcessRemote):
    model = process.Query
    add_name = 'value:api_query_add'
    retrieve_name = 'value:api_query_retrieve'
    update_name = 'value:api_query_update'
    serializer_class = serializer.QuerySerializer

#
# Eval
#
class EvalAddAPIView(AddAPIView):
    serializer_class = serializer.EvalSerializer

class EvalRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Eval
    serializer_class = serializer.EvalSerializer

class EvalUpdateAPIView(base_api.UpdateAPIView):
    model = process.Eval
    serializer_class = serializer.EvalSerializer

class EvalRemote(ProcessRemote):
    model = process.Eval
    add_name = 'value:api_eval_add'
    retrieve_name = 'value:api_eval_retrieve'
    update_name = 'value:api_eval_update'
    serializer_class = serializer.EvalSerializer

#
# Beads
#
class BeadsAddAPIView(AddAPIView):
    serializer_class = serializer.BeadsSerializer

class BeadsRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Beads
    serializer_class = serializer.BeadsSerializer

class BeadsUpdateAPIView(base_api.UpdateAPIView):
    model = process.Beads
    serializer_class = serializer.BeadsSerializer

class BeadsRemote(ProcessRemote):
    model = process.Beads
    add_name = 'value:api_beads_add'
    retrieve_name = 'value:api_beads_retrieve'
    update_name = 'value:api_beads_update'
    serializer_class = serializer.BeadsSerializer
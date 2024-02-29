from django.utils.module_loading import import_string
from config.settings import COLLECT_FILTER_PROCESS
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
    list_name = 'collect:api_process_list'
    retrieve_name = None
    update_name = None
    delete_name = 'collect:api_process_delete'
    serializer_class = serializer.ProcessSerializer
    synchronize = True
    upper_save = True

    def switcher(self, name):
        if name:
            for item in COLLECT_FILTER_PROCESS:
                if item['Model'].split('.')[-1] == name and 'Remote' in item:
                    return import_string(item['Remote'])
        return None

    def data_switcher(self, data):
        return self.switcher(data['name'])

    def model_switcher(self, model):
        return self.switcher(model.name)

#
# Fillna
#
class FillnaAddAPIView(AddAPIView):
    serializer_class = serializer.FillnaSerializer

class FillnaRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Fillna
    serializer_class = serializer.FillnaSerializer

class FillnaUpdateAPIView(base_api.UpdateAPIView):
    model = process.Fillna
    serializer_class = serializer.FillnaSerializer

class FillnaRemote(ProcessRemote):
    model = process.Fillna
    add_name = 'collect:api_fillna_add'
    retrieve_name = 'collect:api_fillna_retrieve'
    update_name = 'collect:api_fillna_update'
    serializer_class = serializer.FillnaSerializer

#
# Dropna
#
class DropnaAddAPIView(AddAPIView):
    serializer_class = serializer.DropnaSerializer

class DropnaRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Dropna
    serializer_class = serializer.DropnaSerializer

class DropnaUpdateAPIView(base_api.UpdateAPIView):
    model = process.Dropna
    serializer_class = serializer.DropnaSerializer

class DropnaRemote(ProcessRemote):
    model = process.Dropna
    add_name = 'collect:api_dropna_add'
    retrieve_name = 'collect:api_dropna_retrieve'
    update_name = 'collect:api_dropna_update'
    serializer_class = serializer.DropnaSerializer

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
    add_name = 'collect:api_drop_add'
    retrieve_name = 'collect:api_drop_retrieve'
    update_name = 'collect:api_drop_update'
    serializer_class = serializer.DropSerializer

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
    add_name = 'collect:api_select_add'
    retrieve_name = 'collect:api_select_retrieve'
    update_name = 'collect:api_select_update'
    serializer_class = serializer.SelectSerializer

#
# Agg
#
class AggAddAPIView(AddAPIView):
    serializer_class = serializer.AggSerializer

class AggRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Agg
    serializer_class = serializer.AggSerializer

class AggUpdateAPIView(base_api.UpdateAPIView):
    model = process.Agg
    serializer_class = serializer.AggSerializer

class AggRemote(ProcessRemote):
    model = process.Agg
    add_name = 'collect:api_agg_add'
    retrieve_name = 'collect:api_agg_retrieve'
    update_name = 'collect:api_agg_update'
    serializer_class = serializer.AggSerializer

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
    add_name = 'collect:api_query_add'
    retrieve_name = 'collect:api_query_retrieve'
    update_name = 'collect:api_query_update'
    serializer_class = serializer.QuerySerializer

#
# Exclude
#
class ExcludeAddAPIView(AddAPIView):
    serializer_class = serializer.ExcludeSerializer

class ExcludeRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Exclude
    serializer_class = serializer.ExcludeSerializer

class ExcludeUpdateAPIView(base_api.UpdateAPIView):
    model = process.Exclude
    serializer_class = serializer.ExcludeSerializer

class ExcludeRemote(ProcessRemote):
    model = process.Exclude
    add_name = 'collect:api_exclude_add'
    retrieve_name = 'collect:api_exclude_retrieve'
    update_name = 'collect:api_exclude_update'
    serializer_class = serializer.ExcludeSerializer

#
# PCAF
#
class PCAFAddAPIView(AddAPIView):
    serializer_class = serializer.PCAFSerializer

class PCAFRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.PCAF
    serializer_class = serializer.PCAFSerializer

class PCAFUpdateAPIView(base_api.UpdateAPIView):
    model = process.PCAF
    serializer_class = serializer.PCAFSerializer

class PCAFRemote(ProcessRemote):
    model = process.PCAF
    add_name = 'collect:api_pcaf_add'
    retrieve_name = 'collect:api_pcaf_retrieve'
    update_name = 'collect:api_pcaf_update'
    serializer_class = serializer.PCAFSerializer

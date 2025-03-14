from django.utils.module_loading import import_string
from config.settings import IMAGE_FILTER_PROCESS
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
    list_name = 'image:api_process_list'
    retrieve_name = None
    update_name = None
    delete_name = 'image:api_process_delete'
    serializer_class = serializer.ProcessSerializer
    synchronize = True
    upper_save = True

    def switcher(self, name):
        if name:
            for item in IMAGE_FILTER_PROCESS:
                if item['Model'].split('.')[-1] == name and 'Remote' in item:
                    return import_string(item['Remote'])
        return None

    def data_switcher(self, data):
        return self.switcher(data['name'])

    def model_switcher(self, model):
        return self.switcher(model.name)

#
# Resize
#
class ResizeAddAPIView(AddAPIView):
    serializer_class = serializer.ResizeSerializer

class ResizeRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Resize
    serializer_class = serializer.ResizeSerializer

class ResizeUpdateAPIView(base_api.UpdateAPIView):
    model = process.Resize
    serializer_class = serializer.ResizeSerializer

class ResizeRemote(ProcessRemote):
    model = process.Resize
    add_name = 'image:api_resize_add'
    retrieve_name = 'image:api_resize_retrieve'
    update_name = 'image:api_resize_update'
    serializer_class = serializer.ResizeSerializer

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
    add_name = 'image:api_trim_add'
    retrieve_name = 'image:api_trim_retrieve'
    update_name = 'image:api_trim_update'
    serializer_class = serializer.TrimSerializer

#
# Smoothing
#
class SmoothingAddAPIView(AddAPIView):
    serializer_class = serializer.SmoothingSerializer

class SmoothingRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Smoothing
    serializer_class = serializer.SmoothingSerializer

class SmoothingUpdateAPIView(base_api.UpdateAPIView):
    model = process.Smoothing
    serializer_class = serializer.SmoothingSerializer

class SmoothingRemote(ProcessRemote):
    model = process.Smoothing
    add_name = 'image:api_smoothing_add'
    retrieve_name = 'image:api_smoothing_retrieve'
    update_name = 'image:api_smoothing_update'
    serializer_class = serializer.SmoothingSerializer

#
# Threshold
#
class ThresholdAddAPIView(AddAPIView):
    serializer_class = serializer.ThresholdSerializer

class ThresholdRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Threshold
    serializer_class = serializer.ThresholdSerializer

class ThresholdUpdateAPIView(base_api.UpdateAPIView):
    model = process.Threshold
    serializer_class = serializer.ThresholdSerializer

class ThresholdRemote(ProcessRemote):
    model = process.Threshold
    add_name = 'image:api_threshold_add'
    retrieve_name = 'image:api_threshold_retrieve'
    update_name = 'image:api_threshold_update'
    serializer_class = serializer.ThresholdSerializer

#
# Molphology
#
class MolphologyAddAPIView(AddAPIView):
    serializer_class = serializer.MolphologySerializer

class MolphologyRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Molphology
    serializer_class = serializer.MolphologySerializer

class MolphologyUpdateAPIView(base_api.UpdateAPIView):
    model = process.Molphology
    serializer_class = serializer.MolphologySerializer

class MolphologyRemote(ProcessRemote):
    model = process.Molphology
    add_name = 'image:api_molphology_add'
    retrieve_name = 'image:api_molphology_retrieve'
    update_name = 'image:api_molphology_update'
    serializer_class = serializer.MolphologySerializer

#
# DrawScale
#
class DrawScaleAddAPIView(AddAPIView):
    serializer_class = serializer.DrawScaleSerializer

class DrawScaleRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.DrawScale
    serializer_class = serializer.DrawScaleSerializer

class DrawScaleUpdateAPIView(base_api.UpdateAPIView):
    model = process.DrawScale
    serializer_class = serializer.DrawScaleSerializer

class DrawScaleRemote(ProcessRemote):
    model = process.DrawScale
    add_name = 'image:api_drawscale_add'
    retrieve_name = 'image:api_drawscale_retrieve'
    update_name = 'image:api_drawscale_update'
    serializer_class = serializer.DrawScaleSerializer

#
# Tone
#
class ToneAddAPIView(AddAPIView):
    serializer_class = serializer.ToneSerializer

class ToneRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Tone
    serializer_class = serializer.ToneSerializer

class ToneUpdateAPIView(base_api.UpdateAPIView):
    model = process.Tone
    serializer_class = serializer.ToneSerializer

class ToneRemote(ProcessRemote):
    model = process.Tone
    add_name = 'image:api_tone_add'
    retrieve_name = 'image:api_tone_retrieve'
    update_name = 'image:api_toen_update'
    serializer_class = serializer.ToneSerializer

#
# Transform
#
class TransformAddAPIView(AddAPIView):
    serializer_class = serializer.TransformSerializer

class TransformRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Transform
    serializer_class = serializer.TransformSerializer

class TransformUpdateAPIView(base_api.UpdateAPIView):
    model = process.Transform
    serializer_class = serializer.TransformSerializer

class TransformRemote(ProcessRemote):
    model = process.Transform
    add_name = 'image:api_transform_add'
    retrieve_name = 'image:api_transform_retrieve'
    update_name = 'image:api_transform_update'
    serializer_class = serializer.TransformSerializer

#
# Draw
#
class DrawAddAPIView(AddAPIView):
    serializer_class = serializer.DrawSerializer

class DrawRetrieveAPIView(base_api.RetrieveAPIView):
    model = process.Draw
    serializer_class = serializer.DrawSerializer

class DrawUpdateAPIView(base_api.UpdateAPIView):
    model = process.Draw
    serializer_class = serializer.DrawSerializer

class DrawRemote(ProcessRemote):
    model = process.Draw
    add_name = 'image:api_draw_add'
    retrieve_name = 'image:api_draw_retrieve'
    update_name = 'image:api_draw_update'
    serializer_class = serializer.DrawSerializer
from django.utils.module_loading import import_string
from django.http import HttpResponse
from django.urls import reverse
from config.settings import FONT_PATH
from project.views import base, base_api, remote
from ..models.plot import Plot
from ..models.area import Area
from ..models.item import Item
from .item import ItemRemote
from ..serializer import AreaSerializer
from io import BytesIO
import urllib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

class AddView(base.AddView):
    model = Area
    upper = Plot
    fields = ('xlabel', 'ylabel', 'xmin', 'xmax', 'ymin', 'ymax', 'legend', 'order')
    template_name = "project/default_add.html"
    bdcl_remove = 1

class UpdateView(base.UpdateView):
    model = Area
    fields = ('xlabel', 'ylabel', 'xmin', 'xmax', 'ymin', 'ymax', 'legend', 'order')
    template_name = "plot/area_update.html"
    bdcl_remove = 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model.objects.get(pk=self.kwargs['pk'])
        items = Item.objects.filter(upper=model).order_by('order')
        item_detail = []
        for item in items:
            detail_url = '/'.join(item.url.split('/')[:-1])
            item_detail.append((item, detail_url))
        context['item_detail'] = item_detail
        return context

    def get_success_url(self):
        return self.object.get_update_url()

class DeleteView(base.DeleteView):
    model = Area
    template_name = "project/default_delete.html"
    bdcl_remove = 1

def AreaPlot(area, host):
    items = Item.objects.filter(upper=area).order_by('order')
    for item in items:
        item.plot(host)
    fp = fm.FontProperties(fname=FONT_PATH)
    plt.xlabel(area.xlabel, fontproperties=fp)
    plt.ylabel(area.ylabel, fontproperties=fp)
    if area.xmin is not None and area.xmax is not None:
        plt.xlim(area.xmin, area.xmax)
    if area.ymin is not None and area.ymax is not None:
        plt.ylim(area.ymin, area.ymax)
    if area.legend == 1:
        plt.legend(loc='best', prop=fp)
    elif area.legend == 2:
        plt.legend(loc='upper right', prop=fp)
    elif area.legend == 3:
        plt.legend(loc='upper left', prop=fp)
    elif area.legend == 4:
        plt.legend(loc='lower left', prop=fp)
    elif area.legend == 5:
        plt.legend(loc='lower right', prop=fp)

class PlotView(base.View):
     model = Area

     def get(self, request, **kwargs):
         area = self.model.objects.get(pk=kwargs['pk'])
         plt.figure()
         AreaPlot(area, self.request._current_scheme_host)
         buf = BytesIO()
         plt.savefig(buf, format='svg', bbox_inches='tight')
         svg = buf.getvalue()
         buf.close()
         plt.close()
         return HttpResponse(svg, content_type='image/svg+xml')

# API
class AddAPIView(base_api.AddAPIView):
    upper = Plot
    serializer_class = AreaSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(updated_by=self.request.user, upper=upper)

class ListAPIView(base_api.ListAPIView):
    upper = Plot
    model = Area
    serializer_class = AreaSerializer

class RetrieveAPIView(base_api.RetrieveAPIView):
    model = Area
    serializer_class = AreaSerializer

class UpdateAPIView(base_api.UpdateAPIView):
    model = Area
    serializer_class = AreaSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = Area
    serializer_class = AreaSerializer

class AreaRemote(remote.Remote):
    model = Area
    add_name = 'plot:api_area_add'
    list_name = 'plot:api_area_list'
    retrieve_name = 'plot:api_area_retrieve'
    update_name = 'plot:api_area_update'
    delete_name = 'plot:api_area_delete'
    serializer_class = AreaSerializer
    synchronize = True
    child_remote = [ItemRemote]

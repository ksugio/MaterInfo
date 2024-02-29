from django.http import HttpResponse
from django.shortcuts import render, redirect
from project.views import base
from ..models.filter import Filter
from ..models.process import Process, Select, Trim, Operate, Rolling, Reduce, Gradient, Drop, Query, Eval, Beads
from io import StringIO, BytesIO
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class AddView(base.AddView):
    model = Process
    upper = Filter
    template_name = "project/default_add.html"
    bdcl_remove = 1

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.updated_by = self.request.user
        model.name = self.model.__name__
        return super().form_valid(form)

class UpdateView(base.UpdateView):
    model = Process
    template_name = "value/process_update.html"
    bdcl_remove = 1

    def get_success_url(self):
        return self.object.get_update_url()

class DeleteView(base.View):
    model = Process
    template_name = 'project/default_delete.html'

    def get(self, request, **kwargs):
        process = self.model.objects.get(pk=kwargs['pk'])
        object = process.entity()
        params = {
            'object': object,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(object, 1)
        }
        return render(request, self.template_name, params)

    def post(self, request, **kwargs):
        process = self.model.objects.get(pk=kwargs['pk'])
        upper = process.upper
        process.delete()
        upper.updated_by = self.request.user
        upper.save()
        return redirect(upper.get_update_url())

class TableView(base.TableView):
    model = Process

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk']).entity()
        if hasattr(model, 'disp') and model.disp != 0:
            plt.figure()
            model.plot()
            buf = BytesIO()
            plt.savefig(buf, format='svg', bbox_inches='tight')
            svg = buf.getvalue()
            buf.close()
            plt.close()
            return HttpResponse(svg, content_type='image/svg+xml')
        else:
            df = model.procval()
            if model.upper.disp_head + model.upper.disp_tail < df.shape[0]:
                df = pd.concat([df.head(model.upper.disp_head), df.tail(model.upper.disp_tail)])
            buf = StringIO()
            df.to_html(buf)
            table = buf.getvalue()
            buf.close()
            return render(request, self.template_name, {'table': table})

#
# Select
#
class SelectAddView(AddView):
    model = Select
    fields = ('columns', 'newnames', 'order')

class SelectUpdateView(UpdateView):
    model = Select
    fields = ('columns', 'newnames', 'order')

#
# Trim
#
class TrimAddView(AddView):
    model = Trim
    fields = ('start_method', 'start_index', 'start_target', 'start_value',
              'end_method', 'end_index', 'end_target', 'end_value',
              'disp', 'order')

class TrimUpdateView(UpdateView):
    model = Trim
    fields = ('start_method', 'start_index', 'start_target', 'start_value',
              'end_method', 'end_index', 'end_target', 'end_value',
              'disp', 'order')

#
# Operate
#
class OperateAddView(AddView):
    model = Operate
    fields = ('method', 'targetcolumn', 'useindex', 'const',
              'column', 'newname', 'replace', 'disp', 'order')

class OperateUpdateView(UpdateView):
    model = Operate
    fields = ('method', 'targetcolumn', 'useindex', 'const',
              'column', 'newname', 'replace', 'disp', 'order')

#
# Rolling
#
class RollingAddView(AddView):
    model = Rolling
    fields = ('method', 'window', 'targetcolumn',
              'center', 'newname', 'replace',
              'disp', 'order')

class RollingUpdateView(UpdateView):
    model = Rolling
    fields = ('method', 'window', 'targetcolumn',
              'center', 'newname', 'replace',
              'disp', 'order')

#
# Reduce
#
class ReduceAddView(AddView):
    model = Reduce
    fields = ('step', 'order')

class ReduceUpdateView(UpdateView):
    model = Reduce
    fields = ('step', 'order')

#
# Gradient
#
class GradientAddView(AddView):
    model = Gradient
    fields = ('x_target', 'y_target', 'newname',
              'disp', 'order')

class GradientUpdateView(UpdateView):
    model = Gradient
    fields = ('x_target', 'y_target', 'newname',
              'disp', 'order')

#
# Drop
#
class DropAddView(AddView):
    model = Drop
    fields = ('columns', 'order')

class DropUpdateView(UpdateView):
    model = Drop
    fields = ('columns', 'order')

#
# Query
#
class QueryAddView(AddView):
    model = Query
    fields = ('condition', 'order')

class QueryUpdateView(UpdateView):
    model = Query
    fields = ('condition', 'order')

#
# Eval
#
class EvalAddView(AddView):
    model = Eval
    fields = ('expr', 'newname', 'order')

class EvalUpdateView(UpdateView):
    model = Eval
    fields = ('expr', 'newname', 'order')

#
# Beads
#
class BeadsAddView(AddView):
    model = Beads
    fields = ('targetcolumn', 'newname', 'withbg',
              'leftext', 'rightext', 'fc', 'amp',
              'disp', 'order')

class BeadsUpdateView(UpdateView):
    model = Beads
    fields = ('targetcolumn', 'newname', 'withbg',
              'leftext', 'rightext', 'fc', 'amp',
              'disp', 'order')

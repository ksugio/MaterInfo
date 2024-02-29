from django.shortcuts import render, redirect
from project.views import base
from ..models.filter import Filter
from ..models import process

class AddView(base.AddView):
    model = process.Process
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
    model = process.Process
    template_name = "image/process_update.html"
    bdcl_remove = 1

    def get_success_url(self):
        return self.object.get_update_url()

class DeleteView(base.View):
    model = process.Process
    template_name = 'project/default_delete.html'

    def get(self, request, **kwargs):
        proc = self.model.objects.get(pk=kwargs['pk'])
        object = proc.entity()
        params = {
            'object': object,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(object, 1)
        }
        return render(request, self.template_name, params)

    def post(self, request, **kwargs):
        proc = self.model.objects.get(pk=kwargs['pk'])
        upper = proc.upper
        proc.delete()
        upper.updated_by = self.request.user
        upper.save()
        return redirect(upper.get_update_url())

#
# Resize
#
class ResizeAddView(AddView):
    model = process.Resize
    fields = ('width', 'height', 'order')

class ResizeUpdateView(UpdateView):
    model = process.Resize
    fields = ('width', 'height', 'order')

#
# Trim
#
class TrimAddView(AddView):
    model = process.Trim
    fields = ('startx', 'starty', 'endx', 'endy', 'order')

class TrimUpdateView(UpdateView):
    model = process.Trim
    fields = ('startx', 'starty', 'endx', 'endy', 'order')

#
# Smoothing
#
class SmoothingAddView(AddView):
    model = process.Smoothing
    fields = ('method', 'size', 'sigma0', 'sigma1', 'order')

class SmoothingUpdateView(UpdateView):
    model = process.Smoothing
    fields = ('method', 'size', 'sigma0', 'sigma1', 'order')

#
# Threshold
#
class ThresholdAddView(AddView):
    model = process.Threshold
    fields = ('method', 'thresh', 'blocksize', 'parameter', 'invert', 'order')

class ThresholdUpdateView(UpdateView):
    model = process.Threshold
    fields = ('method', 'thresh', 'blocksize', 'parameter', 'invert', 'order')

#
# Molphology
#
class MolphologyAddView(AddView):
    model = process.Molphology
    fields = ('method', 'iteration', 'kernelsize', 'order')

class MolphologyUpdateView(UpdateView):
    model = process.Molphology
    fields = ('method', 'iteration', 'kernelsize', 'order')

#
# DrawScale
#
class DrawScaleAddView(AddView):
    model = process.DrawScale
    fields = ('scale', 'width', 'fontsize', 'pos', 'color',
              'marginx', 'marginy', 'bg', 'bgcolor', 'order')

class DrawScaleUpdateView(UpdateView):
    model = process.DrawScale
    fields = ('scale', 'width', 'fontsize', 'pos', 'color',
              'marginx', 'marginy', 'bg', 'bgcolor', 'order')

#
# Tone
#
class ToneAddView(AddView):
    model = process.Tone
    fields = ('method', 'min', 'max', 'low', 'high', 'invert', 'option', 'order')

class ToneUpdateView(UpdateView):
    model = process.Tone
    template_name = "image/tone_update.html"
    fields = ('method', 'min', 'max', 'low', 'high', 'invert', 'option', 'order')

class TonePlotView(base.PlotView):
    model = process.Tone

#
# Transform
#
class TransformAddView(AddView):
    model = process.Transform
    fields = ('method', 'angle', 'order')

class TransformUpdateView(UpdateView):
    model = process.Transform
    fields = ('method', 'angle', 'order')

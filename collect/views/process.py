from django.shortcuts import render, redirect
from project.views import base
from ..models.filter import Filter
from ..models.process import Process, Fillna, Drop, Select, Dropna, Agg, Query, Exclude, PCAF
from ..forms import FillnaForm, DropForm, SelectForm, ExcludeForm, PCAFForm
from io import StringIO

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

class StartEndAddView(AddView):
    def get_form(self, form_class=None):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        choices = upper.upper.columns_choice()
        form.fields['start'].choices = choices
        form.fields['end'].choices = choices
        return form

class MultiAddView(AddView):
    def get_form(self, form_class=None):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        choices = upper.upper.columns_choice()
        form.fields['multi'].choices = choices
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        columns = form.cleaned_data['multi']
        model.columns = ','.join(columns)
        return super().form_valid(form)

class UpdateView(base.UpdateView):
    model = Process
    template_name = "collect/process_update.html"
    bdcl_remove = 1

    def get_success_url(self):
        return self.object.get_update_url()

class StartEndUpdateView(UpdateView):
    def get_form(self, form_class=None):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        choices = model.upper.upper.columns_choice()
        form.fields['start'].choices = choices
        form.fields['start'].initial = model.start
        form.fields['end'].choices = choices
        form.fields['end'].initial = model.end
        return form

class MultiUpdateView(UpdateView):
    def get_form(self, form_class=None):
        model = self.model.objects.get(pk=self.kwargs['pk'])
        form = super().get_form(form_class=form_class)
        choices = model.upper.upper.columns_choice()
        form.fields['multi'].choices = choices
        columns = model.columns.split(',')
        form.fields['multi'].initial = columns
        return form

    def form_valid(self, form):
        model = form.save(commit=False)
        columns = form.cleaned_data['multi']
        model.columns = ','.join(columns)
        return super().form_valid(form)

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

class TableView(base.View):
    model = Process
    template_name = "collect/process_table.html"

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        df, rdf = model.disp_table()
        buf = StringIO()
        df.to_html(buf)
        table = buf.getvalue()
        buf.close()
        if len(rdf) == 0:
            return render(request, self.template_name, {'table': table})
        else:
            buf2 = StringIO()
            rdf.to_html(buf2)
            report = buf2.getvalue()
            buf2.close()
            return render(request, self.template_name, {'table': table, 'report': report})

#
# Fillna
#
class FillnaAddView(StartEndAddView):
    model = Fillna
    form_class = FillnaForm

class FillnaUpdateView(StartEndUpdateView):
    model = Fillna
    form_class = FillnaForm

#
# Dropna
#
class DropnaAddView(AddView):
    model = Dropna
    fields = ('axis', 'how', 'thresh', 'order')

class DropnaUpdateView(UpdateView):
    model = Dropna
    fields = ('axis', 'how', 'thresh', 'order')

#
# Drop
#
class DropAddView(StartEndAddView):
    model = Drop
    form_class = DropForm

class DropUpdateView(StartEndUpdateView):
    model = Drop
    form_class = DropForm

#
# Select
#
class SelectAddView(MultiAddView):
    model = Select
    form_class = SelectForm

class SelectUpdateView(MultiUpdateView):
    model = Select
    form_class = SelectForm

# Agg
#
class AggAddView(AddView):
    model = Agg
    fields = ('groupby', 'method', 'order')

class AggUpdateView(UpdateView):
    model = Agg
    fields = ('groupby', 'method', 'order')

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
# Exclude
#
class ExcludeAddView(StartEndAddView):
    model = Exclude
    form_class = ExcludeForm

class ExcludeUpdateView(StartEndUpdateView):
    model = Exclude
    form_class = ExcludeForm

#
# PCAF
#
class PCAFAddView(StartEndAddView):
    model = PCAF
    form_class = PCAFForm

class PCAFUpdateView(StartEndUpdateView):
    model = PCAF
    form_class = PCAFForm


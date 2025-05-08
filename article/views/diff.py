from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from project.views import base, base_api, remote
from diff_match_patch import diff_match_patch
from ..models import Article, Diff
from ..serializer import DiffSerializer
from ..latex import Tex2PDF

def CreateDiff(current, previous, upper, user, comment=''):
    dmp = diff_match_patch()
    patches = dmp.patch_make(current, previous)
    if len(patches) > 0:
        diff = dmp.patch_toText(patches)
        Diff.objects.create(upper=upper, updated_by=user, diff=diff, comment=comment)

def PreviousText(model):
    diffs = Diff.objects.filter(upper=model.upper).order_by('-updated_at')
    text = model.upper.text
    dmp = diff_match_patch()
    for diff in diffs:
        patches = dmp.patch_fromText(diff.diff)
        text, _ = dmp.patch_apply(patches, text)
        if diff.id == model.id:
            break
    return text

class DiffPreviousView(base.View):
    model = Diff
    template_name = "article/diff_previous.html"

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        params = {
            'object': model,
            'previous_text': PreviousText(model),
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(model)
        }
        return render(request, self.template_name, params)

class DiffDiffView(base.View):
    model = Diff
    template_name = "article/diff_diff.html"

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        previous = PreviousText(model)
        dmp = diff_match_patch()
        diff = dmp.diff_main(previous, model.upper.text)
        pretty = dmp.diff_prettyHtml(diff)
        params = {
            'object': model,
            'pretty': pretty,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(model)
        }
        return render(request, self.template_name, params)

class DiffRestoreView(base.View):
    model = Diff
    template_name = "article/diff_restore.html"

    def get(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        params = {
            'object': model,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(model)
        }
        return render(request, self.template_name, params)

    def post(self, request, **kwargs):
        model = self.model.objects.get(pk=kwargs['pk'])
        previous = model.upper.text
        model.upper.text = PreviousText(model)
        comment = model.upper.comment
        model.upper.comment = 'Restore : ' + model.comment
        if model.upper.type == 1:
            pdfv, _, _ = Tex2PDF(model.upper, model.upper.text, self.request)
            if pdfv:
                model.upper.file = InMemoryUploadedFile(ContentFile(pdfv), None, 'ArticleFile.pdf',
                                                        None, len(pdfv), None)
            else:
                model.upper.file = None
        model.upper.save()
        CreateDiff(model.upper.text, previous, model.upper, self.request.user, comment)
        return redirect(model.upper.get_detail_url())

# API
class DiffAddAPIView(base_api.AddAPIView):
    upper = Article
    serializer_class = DiffSerializer

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        serializer.save(updated_by=self.request.user, upper=upper)

class DiffListAPIView(base_api.ListAPIView):
    upper = Article
    model = Diff
    serializer_class = DiffSerializer

class DiffRetrieveAPIView(base_api.RetrieveAPIView):
    model = Diff
    serializer_class = DiffSerializer

class DiffUpdateAPIView(base_api.UpdateAPIView):
    model = Diff
    serializer_class = DiffSerializer

class DiffDeleteAPIView(base_api.DeleteAPIView):
    model = Diff
    serializer_class = DiffSerializer

class DiffRemote(remote.Remote):
    model = Diff
    add_name = 'article:api_diff_add'
    list_name = 'article:api_diff_list'
    retrieve_name = 'article:api_diff_retrieve'
    update_name = 'article:api_diff_update'
    delete_name = 'article:api_diff_delete'
    serializer_class = DiffSerializer
    synchronize = True

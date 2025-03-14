from django.urls import path
from .views import (
    collect, filter, process, process_api, reduction, correlation, clustering, classification,
    regression, inverse, regreshap, classshap, regrepred, classpred
)

app_name = 'collect'
urlpatterns = [
    path('<int:pk>/add', collect.AddView.as_view(), name='add'),
    path('<int:pk>/upload', collect.UploadView.as_view(), name='upload'),
    path('<int:pk>/get', collect.GetView.as_view(), name='get'),
    path('<int:pk>/import', collect.ImportView.as_view(), name='import'),
    path('<int:pk>/list', collect.ListView.as_view(), name='list'),
    path('<int:pk>/search', collect.SearchView.as_view(), name='search'),
    path('collect/<int:pk>', collect.DetailView.as_view(), name='detail'),
    path('collect/<int:pk>/update', collect.UpdateView.as_view(), name='update'),
    path('collect/<int:pk>/edit_note', collect.EditNoteView.as_view(), name='edit_note'),
    path('collect/<int:pk>/delete', collect.DeleteView.as_view(), name='delete'),
    path('collect/<str:unique>/file', collect.FileView.as_view(), name='file'),
    path('collect/<int:pk>/update_upper_updated', collect.UpdateUpperUpdatedView.as_view(), name='update_upper_updated'),
    path('collect/<int:pk>/table/<str:name>', collect.TableView.as_view(), name='table'),
    # API
    path('api/<int:pk>/add', collect.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', collect.ListAPIView.as_view(), name='api_list'),
    path('api/collect/<int:pk>', collect.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/collect/<int:pk>/update', collect.UpdateAPIView.as_view(), name='api_update'),
    path('api/collect/<int:pk>/delete', collect.DeleteAPIView.as_view(), name='api_delete'),
    path('api/collect/<int:pk>/file', collect.FileAPIView.as_view(), name='api_file'),
    # Filter
    path('collect/<int:pk>/filter/add', filter.AddView.as_view(), name='filter_add'),
    path('collect/<int:pk>/filter/import', filter.ImportView.as_view(), name='filter_import'),
    path('collect/<int:pk>/filter/list', filter.ListView.as_view(), name='filter_list'),
    path('filter/<int:pk>', filter.DetailView.as_view(), name='filter_detail'),
    path('filter/<int:pk>/update', filter.UpdateView.as_view(), name='filter_update'),
    path('filter/<int:pk>/edit_note', filter.EditNoteView.as_view(), name='filter_edit_note'),
    path('filter/<int:pk>/delete', filter.DeleteView.as_view(), name='filter_delete'),
    path('filter/<str:unique>/file', filter.FileView.as_view(), name='filter_file'),
    path('filter/<int:pk>/table', filter.TableView.as_view(), name='filter_table'),
    path('filter/<int:pk>/plot/<str:name>', filter.PlotView.as_view(), name='filter_plot'),
    # Filter API
    path('api/collect/<int:pk>/filter/add', filter.AddAPIView.as_view(), name='api_filter_add'),
    path('api/collect/<int:pk>/filter/list', filter.ListAPIView.as_view(), name='api_filter_list'),
    path('api/filter/<int:pk>', filter.RetrieveAPIView.as_view(), name='api_filter_retrieve'),
    path('api/filter/<int:pk>/update', filter.UpdateAPIView.as_view(), name='api_filter_update'),
    path('api/filter/<int:pk>/delete', filter.DeleteAPIView.as_view(), name='api_filter_delete'),
    path('api/filter/<int:pk>/file', filter.FileAPIView.as_view(), name='api_filter_file'),
    # Process
    path('process/<int:pk>/table', process.TableView.as_view(), name='process_table'),
    path('process/<int:pk>/delete', process.DeleteView.as_view(), name='process_delete'),
    path('filter/<int:pk>/fillna/add', process.FillnaAddView.as_view(), name='fillna_add'),
    path('fillna/<int:pk>/update', process.FillnaUpdateView.as_view(), name='fillna_update'),
    path('filter/<int:pk>/dropna/add', process.DropnaAddView.as_view(), name='dropna_add'),
    path('dropna/<int:pk>/update', process.DropnaUpdateView.as_view(), name='dropna_update'),
    path('filter/<int:pk>/drop/add', process.DropAddView.as_view(), name='drop_add'),
    path('drop/<int:pk>/update', process.DropUpdateView.as_view(), name='drop_update'),
    path('filter/<int:pk>/select/add', process.SelectAddView.as_view(), name='select_add'),
    path('select/<int:pk>/update', process.SelectUpdateView.as_view(), name='select_update'),
    path('filter/<int:pk>/agg/add', process.AggAddView.as_view(), name='agg_add'),
    path('agg/<int:pk>/update', process.AggUpdateView.as_view(), name='agg_update'),
    path('filter/<int:pk>/query/add', process.QueryAddView.as_view(), name='query_add'),
    path('query/<int:pk>/update', process.QueryUpdateView.as_view(), name='query_update'),
    path('filter/<int:pk>/exclude/add', process.ExcludeAddView.as_view(), name='exclude_add'),
    path('exclude/<int:pk>/update', process.ExcludeUpdateView.as_view(), name='exclude_update'),
    path('filter/<int:pk>/pcaf/add', process.PCAFAddView.as_view(), name='pcaf_add'),
    path('pcaf/<int:pk>/update', process.PCAFUpdateView.as_view(), name='pcaf_update'),
    # Process API
    path('api/filter/<int:pk>/process/list', process_api.ListAPIView.as_view(), name='api_process_list'),
    path('api/process/<int:pk>/delete', process_api.DeleteAPIView.as_view(), name='api_process_delete'),
    path('api/filter/<int:pk>/fillna/add', process_api.FillnaAddAPIView.as_view(), name='api_fillna_add'),
    path('api/fillna/<int:pk>', process_api.FillnaRetrieveAPIView.as_view(), name='api_fillna_retrieve'),
    path('api/fillna/<int:pk>/update', process_api.FillnaUpdateAPIView.as_view(), name='api_fillna_update'),
    path('api/filter/<int:pk>/dropna/add', process_api.DropnaAddAPIView.as_view(), name='api_dropna_add'),
    path('api/dropna/<int:pk>', process_api.DropnaRetrieveAPIView.as_view(), name='api_dropna_retrieve'),
    path('api/dropna/<int:pk>/update', process_api.DropnaUpdateAPIView.as_view(), name='api_dropna_update'),
    path('api/filter/<int:pk>/drop/add', process_api.DropAddAPIView.as_view(), name='api_drop_add'),
    path('api/drop/<int:pk>', process_api.DropRetrieveAPIView.as_view(), name='api_drop_retrieve'),
    path('api/drop/<int:pk>/update', process_api.DropUpdateAPIView.as_view(), name='api_drop_update'),
    path('api/filter/<int:pk>/select/add', process_api.SelectAddAPIView.as_view(), name='api_select_add'),
    path('api/select/<int:pk>', process_api.SelectRetrieveAPIView.as_view(), name='api_select_retrieve'),
    path('api/select/<int:pk>/update', process_api.SelectUpdateAPIView.as_view(), name='api_select_update'),
    path('api/filter/<int:pk>/agg/add', process_api.AggAddAPIView.as_view(), name='api_agg_add'),
    path('api/agg/<int:pk>', process_api.AggRetrieveAPIView.as_view(), name='api_agg_retrieve'),
    path('api/agg/<int:pk>/update', process_api.AggUpdateAPIView.as_view(), name='api_agg_update'),
    path('api/filter/<int:pk>/query/add', process_api.QueryAddAPIView.as_view(), name='api_query_add'),
    path('api/query/<int:pk>', process_api.QueryRetrieveAPIView.as_view(), name='api_query_retrieve'),
    path('api/query/<int:pk>/update', process_api.QueryUpdateAPIView.as_view(), name='api_query_update'),
    path('api/filter/<int:pk>/exclude/add', process_api.ExcludeAddAPIView.as_view(), name='api_exclude_add'),
    path('api/exclude/<int:pk>', process_api.ExcludeRetrieveAPIView.as_view(), name='api_exclude_retrieve'),
    path('api/exclude/<int:pk>/update', process_api.ExcludeUpdateAPIView.as_view(), name='api_exclude_update'),
    path('api/filter/<int:pk>/pcaf/add', process_api.PCAFAddAPIView.as_view(), name='api_pcaf_add'),
    path('api/pcaf/<int:pk>', process_api.PCAFRetrieveAPIView.as_view(), name='api_pcaf_retrieve'),
    path('api/pcaf/<int:pk>/update', process_api.PCAFUpdateAPIView.as_view(), name='api_pcaf_update'),
    # Reduction
    path('filter/<int:pk>/reduction/add', reduction.AddView.as_view(), name='reduction_add'),
    path('filter/<int:pk>/reduction/list', reduction.ListView.as_view(), name='reduction_list'),
    path('reduction/<int:pk>', reduction.DetailView.as_view(), name='reduction_detail'),
    path('reduction/<int:pk>/update', reduction.UpdateView.as_view(), name='reduction_update'),
    path('reduction/<int:pk>/edit_note', reduction.EditNoteView.as_view(), name='reduction_edit_note'),
    path('reduction/<int:pk>/delete', reduction.DeleteView.as_view(), name='reduction_delete'),
    path('reduction/<str:unique>/file', reduction.FileView.as_view(), name='reduction_file'),
    path('reduction/<int:pk>/plot/scatter', reduction.PlotScatterView.as_view(), name='reduction_plot_scatter'),
    path('reduction/<int:pk>/plot/components', reduction.PlotComponentsView.as_view(), name='reduction_plot_components'),
    # Reduction API
    path('api/filter/<int:pk>/reduction/add', reduction.AddAPIView.as_view(), name='api_reduction_add'),
    path('api/filter/<int:pk>/reduction/list', reduction.ListAPIView.as_view(), name='api_reduction_list'),
    path('api/reduction/<int:pk>', reduction.RetrieveAPIView.as_view(), name='api_reduction_retrieve'),
    path('api/reduction/<int:pk>/update', reduction.UpdateAPIView.as_view(), name='api_reduction_update'),
    path('api/reduction/<int:pk>/delete', reduction.DeleteAPIView.as_view(), name='api_reduction_delete'),
    path('api/reduction/<int:pk>/file', reduction.FileAPIView.as_view(), name='api_reduction_file'),
    # Correlation
    path('filter/<int:pk>/correlation/add', correlation.AddView.as_view(), name='correlation_add'),
    path('filter/<int:pk>/correlation/list', correlation.ListView.as_view(), name='correlation_list'),
    path('correlation/<int:pk>', correlation.DetailView.as_view(), name='correlation_detail'),
    path('correlation/<int:pk>/update', correlation.UpdateView.as_view(), name='correlation_update'),
    path('correlation/<int:pk>/edit_note', correlation.EditNoteView.as_view(), name='correlation_edit_note'),
    path('correlation/<int:pk>/delete', correlation.DeleteView.as_view(), name='correlation_delete'),
    path('correlation/<int:pk>/file', correlation.FileView.as_view(), name='correlation_file'),
    path('correlation/<int:pk>/heatmap', correlation.HeatmapView.as_view(), name='correlation_heatmap'),
    path('correlation/<int:pk>/scatter/<str:feat1>/<str:feat2>', correlation.ScatterView.as_view(), name='correlation_scatter'),
    # Correlation API
    path('api/filter/<int:pk>/correlation/add', correlation.AddAPIView.as_view(), name='api_correlation_add'),
    path('api/filter/<int:pk>/correlation/list', correlation.ListAPIView.as_view(), name='api_correlation_list'),
    path('api/correlation/<int:pk>', correlation.RetrieveAPIView.as_view(), name='api_correlation_retrieve'),
    path('api/correlation/<int:pk>/update', correlation.UpdateAPIView.as_view(), name='api_correlation_update'),
    path('api/correlation/<int:pk>/delete', correlation.DeleteAPIView.as_view(), name='api_correlation_delete'),
    path('api/correlation/<int:pk>/file', correlation.FileAPIView.as_view(), name='api_correlation_file'),
    # Clustering
    path('filter/<int:pk>/clustering/add', clustering.AddView.as_view(), name='clustering_add'),
    path('filter/<int:pk>/clustering/list', clustering.ListView.as_view(), name='clustering_list'),
    path('clustering/<int:pk>', clustering.DetailView.as_view(), name='clustering_detail'),
    path('clustering/<int:pk>/update', clustering.UpdateView.as_view(), name='clustering_update'),
    path('clustering/<int:pk>/edit_note', clustering.EditNoteView.as_view(), name='clustering_edit_note'),
    path('clustering/<int:pk>/delete', clustering.DeleteView.as_view(), name='clustering_delete'),
    path('clustering/<str:unique>/file', clustering.FileView.as_view(), name='clustering_file'),
    path('clustering/<int:pk>/plot', clustering.PlotView.as_view(), name='clustering_plot'),
    path('clustering/<int:pk>/plot/trials/<str:name>', clustering.PlotTrialsView.as_view(), name='clustering_plot_trials'),
    # Clustering API
    path('api/filter/<int:pk>/clustering/add', clustering.AddAPIView.as_view(), name='api_clustering_add'),
    path('api/filter/<int:pk>/clustering/list', clustering.ListAPIView.as_view(), name='api_clustering_list'),
    path('api/clustering/<int:pk>', clustering.RetrieveAPIView.as_view(), name='api_clustering_retrieve'),
    path('api/clustering/<int:pk>/update', clustering.UpdateAPIView.as_view(), name='api_clustering_update'),
    path('api/clustering/<int:pk>/delete', clustering.DeleteAPIView.as_view(), name='api_clustering_delete'),
    path('api/clustering/<int:pk>/file', clustering.FileAPIView.as_view(), name='api_clustering_file'),
    # Classification
    path('filter/<int:pk>/classification/add', classification.AddView.as_view(), name='classification_add'),
    path('filter/<int:pk>/classification/list', classification.ListView.as_view(), name='classification_list'),
    path('classification/<int:pk>', classification.DetailView.as_view(), name='classification_detail'),
    path('classification/<int:pk>/update', classification.UpdateView.as_view(), name='classification_update'),
    path('classification/<int:pk>/edit_note', classification.EditNoteView.as_view(), name='classification_edit_note'),
    path('classification/<int:pk>/delete', classification.DeleteView.as_view(), name='classification_delete'),
    path('classification/<int:pk>/revoke', classification.RevokeView.as_view(), name='classification_revoke'),
    path('classification/<int:pk>/onnx', classification.ONNXView.as_view(), name='classification_onnx'),
    path('classification/<int:pk>/file', classification.FileView.as_view(), name='classification_file'),
    path('classification/<int:pk>/plot/importance', classification.PlotImportanceView.as_view(), name='classification_plot_importance'),
    path('classification/<int:pk>/plot/trials/<str:name>', classification.PlotTrialsView.as_view(), name='classification_plot_trials'),
    path('classification/<int:pk>/report/<int:rid>', classification.ReportView.as_view(), name='classification_report'),
    # Classification API
    path('api/filter/<int:pk>/classification/add', classification.AddAPIView.as_view(), name='api_classification_add'),
    path('api/filter/<int:pk>/classification/list', classification.ListAPIView.as_view(), name='api_classification_list'),
    path('api/classification/<int:pk>', classification.RetrieveAPIView.as_view(), name='api_classification_retrieve'),
    path('api/classification/<int:pk>/update', classification.UpdateAPIView.as_view(), name='api_classification_update'),
    path('api/classification/<int:pk>/delete', classification.DeleteAPIView.as_view(), name='api_classification_delete'),
    path('api/classification/<int:pk>/file', classification.FileAPIView.as_view(), name='api_classification_file'),
    # Regression
    path('filter/<int:pk>/regression/add', regression.AddView.as_view(), name='regression_add'),
    path('filter/<int:pk>/regression/list', regression.ListView.as_view(), name='regression_list'),
    path('regression/<int:pk>', regression.DetailView.as_view(), name='regression_detail'),
    path('regression/<int:pk>/update', regression.UpdateView.as_view(), name='regression_update'),
    path('regression/<int:pk>/edit_note', regression.EditNoteView.as_view(), name='regression_edit_note'),
    path('regression/<int:pk>/delete', regression.DeleteView.as_view(), name='regression_delete'),
    path('regression/<int:pk>/revoke', regression.RevokeView.as_view(), name='regression_revoke'),
    path('regression/<int:pk>/onnx', regression.ONNXView.as_view(), name='regression_onnx'),
    path('regression/<str:unique>/file', regression.FileView.as_view(), name='regression_file'),
    path('regression/<int:pk>/file2', regression.File2View.as_view(), name='regression_file2'),
    path('regression/<int:pk>/plot/<int:pid>', regression.PlotView.as_view(), name='regression_plot'),
    path('regression/<int:pk>/plot/all', regression.PlotAllView.as_view(), name='regression_plot_all'),
    path('regression/<int:pk>/plot/importance', regression.PlotImportanceView.as_view(), name='regression_plot_importance'),
    path('regression/<int:pk>/plot/trials/<str:name>', regression.PlotTrialsView.as_view(), name='regression_plot_trials'),
    # Regression API
    path('api/filter/<int:pk>/regression/add', regression.AddAPIView.as_view(), name='api_regression_add'),
    path('api/filter/<int:pk>/regression/list', regression.ListAPIView.as_view(), name='api_regression_list'),
    path('api/regression/<int:pk>', regression.RetrieveAPIView.as_view(), name='api_regression_retrieve'),
    path('api/regression/<int:pk>/update', regression.UpdateAPIView.as_view(), name='api_regression_update'),
    path('api/regression/<int:pk>/delete', regression.DeleteAPIView.as_view(), name='api_regression_delete'),
    path('api/regression/<int:pk>/file', regression.FileAPIView.as_view(), name='api_regression_file'),
    path('api/regression/<int:pk>/file2', regression.File2APIView.as_view(), name='api_regression_file2'),
    # Inverse
    path('filter/<int:pk>/inverse/add', inverse.AddView.as_view(), name='inverse_add'),
    path('filter/<int:pk>/inverse/list', inverse.ListView.as_view(), name='inverse_list'),
    path('inverse/<int:pk>', inverse.DetailView.as_view(), name='inverse_detail'),
    path('inverse/<int:pk>/update', inverse.UpdateView.as_view(), name='inverse_update'),
    path('inverse/<int:pk>/edit_note', inverse.EditNoteView.as_view(), name='inverse_edit_note'),
    path('inverse/<int:pk>/delete', inverse.DeleteView.as_view(), name='inverse_delete'),
    path('inverse/<int:pk>/revoke', inverse.RevokeView.as_view(), name='inverse_revoke'),
    path('inverse/<int:pk>/file', inverse.FileView.as_view(), name='inverse_file'),
    path('inverse/<int:pk>/table', inverse.TableView.as_view(), name='inverse_table'),
    path('inverse/<int:pk>/plot', inverse.PlotView.as_view(), name='inverse_plot'),
    # Inverse API
    path('api/filter/<int:pk>/inverse/add', inverse.AddAPIView.as_view(), name='api_inverse_add'),
    path('api/filter/<int:pk>/inverse/list', inverse.ListAPIView.as_view(), name='api_inverse_list'),
    path('api/inverse/<int:pk>', inverse.RetrieveAPIView.as_view(), name='api_inverse_retrieve'),
    path('api/inverse/<int:pk>/update', inverse.UpdateAPIView.as_view(), name='api_inverse_update'),
    path('api/inverse/<int:pk>/delete', inverse.DeleteAPIView.as_view(), name='api_inverse_delete'),
    path('api/inverse/<int:pk>/file', inverse.FileAPIView.as_view(), name='api_inverse_file'),
    # RegreSHAP
    path('regression/<int:pk>/regreshap/add', regreshap.AddView.as_view(), name='regreshap_add'),
    path('regression/<int:pk>/regreshap/list', regreshap.ListView.as_view(), name='regreshap_list'),
    path('regreshap/<int:pk>', regreshap.DetailView.as_view(), name='regreshap_detail'),
    path('regreshap/<int:pk>/update', regreshap.UpdateView.as_view(), name='regreshap_update'),
    path('regreshap/<int:pk>/edit_note', regreshap.EditNoteView.as_view(), name='regreshap_edit_note'),
    path('regreshap/<int:pk>/delete', regreshap.DeleteView.as_view(), name='regreshap_delete'),
    path('regreshap/<int:pk>/revoke', regreshap.RevokeView.as_view(), name='regreshap_revoke'),
    path('regreshap/<int:pk>/plot', regreshap.PlotView.as_view(), name='regreshap_plot'),
    path('regreshap/<int:pk>/plot/dependence/<str:name>', regreshap.PlotDependenceView.as_view(), name='regreshap_plot_dependence'),
    # RegreSHAP API
    path('api/regression/<int:pk>/regreshap/add', regreshap.AddAPIView.as_view(), name='api_regreshap_add'),
    path('api/regression/<int:pk>/regreshap/list', regreshap.ListAPIView.as_view(), name='api_regreshap_list'),
    path('api/regreshap/<int:pk>', regreshap.RetrieveAPIView.as_view(), name='api_regreshap_retrieve'),
    path('api/regreshap/<int:pk>/update', regreshap.UpdateAPIView.as_view(), name='api_regreshap_update'),
    path('api/regreshap/<int:pk>/delete', regreshap.DeleteAPIView.as_view(), name='api_regreshap_delete'),
    # Classification SHAP
    path('classification/<int:pk>/classshap/add', classshap.AddView.as_view(), name='classshap_add'),
    path('classification/<int:pk>/classshap/list', classshap.ListView.as_view(), name='classshap_list'),
    path('classshap/<int:pk>', classshap.DetailView.as_view(), name='classshap_detail'),
    path('classshap/<int:pk>/update', classshap.UpdateView.as_view(), name='classshap_update'),
    path('classshap/<int:pk>/edit_note', classshap.EditNoteView.as_view(), name='classshap_edit_note'),
    path('classshap/<int:pk>/delete', classshap.DeleteView.as_view(), name='classshap_delete'),
    path('classshap/<int:pk>/revoke', classshap.RevokeView.as_view(), name='classshap_revoke'),
    path('classshap/<int:pk>/plot', classshap.PlotView.as_view(), name='classshap_plot'),
    # ClassSHAP API
    path('api/classification/<int:pk>/classshap/add', classshap.AddAPIView.as_view(), name='api_classshap_add'),
    path('api/classification/<int:pk>/classshap/list', classshap.ListAPIView.as_view(), name='api_classshap_list'),
    path('api/classshap/<int:pk>', classshap.RetrieveAPIView.as_view(), name='api_classshap_retrieve'),
    path('api/classshap/<int:pk>/update', classshap.UpdateAPIView.as_view(), name='api_classshap_update'),
    path('api/classshap/<int:pk>/delete', classshap.DeleteAPIView.as_view(), name='api_classshap_delete'),
    # RegrePred
    path('regression/<int:pk>/regrepred/add', regrepred.AddView.as_view(), name='regrepred_add'),
    path('regression/<int:pk>/regrepred/list', regrepred.ListView.as_view(), name='regrepred_list'),
    path('regrepred/<int:pk>', regrepred.DetailView.as_view(), name='regrepred_detail'),
    path('regrepred/<int:pk>/update', regrepred.UpdateView.as_view(), name='regrepred_update'),
    path('regrepred/<int:pk>/edit_note', regrepred.EditNoteView.as_view(), name='regrepred_edit_note'),
    path('regrepred/<int:pk>/delete', regrepred.DeleteView.as_view(), name='regrepred_delete'),
    path('regrepred/<int:pk>/table', regrepred.TableView.as_view(), name='regrepred_table'),
    path('regrepred/<int:pk>/download', regrepred.DownloadView.as_view(), name='regrepred_download'),
    # RegrePred API
    path('api/regression/<int:pk>/regrepred/add', regrepred.AddAPIView.as_view(), name='api_regrepred_add'),
    path('api/regression/<int:pk>/regrepred/list', regrepred.ListAPIView.as_view(), name='api_regrepred_list'),
    path('api/regrepred/<int:pk>', regrepred.RetrieveAPIView.as_view(), name='api_regrepred_retrieve'),
    path('api/regrepred/<int:pk>/update', regrepred.UpdateAPIView.as_view(), name='api_regrepred_update'),
    path('api/regrepred/<int:pk>/delete', regrepred.DeleteAPIView.as_view(), name='api_regrepred_delete'),
    path('api/regrepred/<int:pk>/file', regrepred.FileAPIView.as_view(), name='api_regrepred_file'),
    # ClassPred
    path('classification/<int:pk>/classpred/add', classpred.AddView.as_view(), name='classpred_add'),
    path('classification/<int:pk>/classpred/list', classpred.ListView.as_view(), name='classpred_list'),
    path('classpred/<int:pk>', classpred.DetailView.as_view(), name='classpred_detail'),
    path('classpred/<int:pk>/update', classpred.UpdateView.as_view(), name='classpred_update'),
    path('classpred/<int:pk>/edit_note', classpred.EditNoteView.as_view(), name='classpred_edit_note'),
    path('classpred/<int:pk>/delete', classpred.DeleteView.as_view(), name='classpred_delete'),
    path('classpred/<int:pk>/table', classpred.TableView.as_view(), name='classpred_table'),
    path('classpred/<int:pk>/download', classpred.DownloadView.as_view(), name='classpred_download'),
    # ClassPred API
    path('api/classification/<int:pk>/classpred/add', classpred.AddAPIView.as_view(), name='api_classpred_add'),
    path('api/classification/<int:pk>/classpred/list', classpred.ListAPIView.as_view(), name='api_classpred_list'),
    path('api/classpred/<int:pk>', classpred.RetrieveAPIView.as_view(), name='api_classpred_retrieve'),
    path('api/classpred/<int:pk>/update', classpred.UpdateAPIView.as_view(), name='api_classpred_update'),
    path('api/classpred/<int:pk>/delete', classpred.DeleteAPIView.as_view(), name='api_classpred_delete'),
    path('api/classpred/<int:pk>/file', classpred.FileAPIView.as_view(), name='api_classpred_file'),
]

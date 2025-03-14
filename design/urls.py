from django.urls import path
from .views import design, condition, experiment

app_name = 'design'
urlpatterns = [
    path('<int:pk>/add', design.AddView.as_view(), name='add'),
    path('<int:pk>/import', design.ImportView.as_view(), name='import'),
    path('<int:pk>/list', design.ListView.as_view(), name='list'),
    path('design/<int:pk>', design.DetailView.as_view(), name='detail'),
    path('design/<int:pk>/update', design.UpdateView.as_view(), name='update'),
    path('design/<int:pk>/edit_note', design.EditNoteView.as_view(), name='edit_note'),
    path('design/<int:pk>/delete', design.DeleteView.as_view(), name='delete'),
    path('design/<int:pk>/table', design.TableView.as_view(), name='table'),
    path('design/<int:pk>/plot', design.PlotView.as_view(), name='plot'),
    # API
    path('api/<int:pk>/add', design.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', design.ListAPIView.as_view(), name='api_list'),
    path('api/design/<int:pk>', design.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/design/<int:pk>/update', design.UpdateAPIView.as_view(), name='api_update'),
    path('api/design/<int:pk>/delete', design.DeleteAPIView.as_view(), name='api_delete'),
    path('api/design/<int:pk>/file', design.FileAPIView.as_view(), name='api_file'),
    # Condition
    path('design/<int:pk>/condition/add', condition.AddView.as_view(), name='condition_add'),
    path('condition/<int:pk>/update', condition.UpdateView.as_view(), name='condition_update'),
    path('condition/<int:pk>/delete', condition.DeleteView.as_view(), name='condition_delete'),
    # Condition API
    path('api/design/<int:pk>/condition/add', condition.AddAPIView.as_view(), name='api_condition_add'),
    path('api/design/<int:pk>/condition/list', condition.ListAPIView.as_view(), name='api_condition_list'),
    path('api/condition/<int:pk>', condition.RetrieveAPIView.as_view(), name='api_condition_retrieve'),
    path('api/condition/<int:pk>/update', condition.UpdateAPIView.as_view(), name='api_condition_update'),
    path('api/condition/<int:pk>/delete', condition.DeleteAPIView.as_view(), name='api_condition_delete'),
    # Experiment
    path('design/<int:pk>/experiment/add', experiment.AddView.as_view(), name='experiment_add'),
    path('design/<int:pk>/experiment/doptimal', experiment.DOptimalView.as_view(), name='experiment_doptimal'),
    path('design/<int:pk>/experiment/bayesian', experiment.BayesianView.as_view(), name='experiment_bayesian'),
    path('design/<int:pk>/experiment/list', experiment.ListView.as_view(), name='experiment_list'),
    path('experiment/<int:pk>/update', experiment.UpdateView.as_view(), name='experiment_update'),
    path('experiment/<int:pk>/delete', experiment.DeleteView.as_view(), name='experiment_delete'),
    path('experiment/<int:pk>/add_sample', experiment.AddSampleView.as_view(), name='experiment_add_sample'),
    # Experiment API
    path('api/design/<int:pk>/experiment/add', experiment.AddAPIView.as_view(), name='api_experiment_add'),
    path('api/design/<int:pk>/experiment/list', experiment.ListAPIView.as_view(), name='api_experiment_list'),
    path('api/experiment/<int:pk>', experiment.RetrieveAPIView.as_view(), name='api_experiment_retrieve'),
    path('api/experiment/<int:pk>/update', experiment.UpdateAPIView.as_view(), name='api_experiment_update'),
    path('api/experiment/<int:pk>/delete', experiment.DeleteAPIView.as_view(), name='api_experiment_delete'),
]
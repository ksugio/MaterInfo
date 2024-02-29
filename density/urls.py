from django.urls import path
from . import views

app_name = 'density'
urlpatterns = [
    path('<int:pk>/add', views.AddView.as_view(), name='add'),
    path('<int:pk>/import', views.ImportView.as_view(), name='import'),
    path('<int:pk>/list', views.ListView.as_view(), name='list'),
    path('density/<int:pk>', views.DetailView.as_view(), name='detail'),
    path('density/<int:pk>/update', views.UpdateView.as_view(), name='update'),
    path('density/<int:pk>/delete', views.DeleteView.as_view(), name='delete'),
    path('density/<int:pk>/edit_note', views.EditNoteView.as_view(), name='edit_note'),
    # API
    path('api/<int:pk>/add', views.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', views.ListAPIView.as_view(), name='api_list'),
    path('api/density/<int:pk>', views.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/density/<int:pk>/update', views.UpdateAPIView.as_view(), name='api_update'),
]

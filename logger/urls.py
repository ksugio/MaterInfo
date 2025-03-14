from django.urls import path
from .views import logger

app_name = 'logger'
urlpatterns = [
    path('<int:pk>/add', logger.AddView.as_view(), name='add'),
    path('<int:pk>/list', logger.ListView.as_view(), name='list'),
    path('logger/<int:pk>', logger.DetailView.as_view(), name='detail'),
    path('logger/<int:pk>/update', logger.UpdateView.as_view(), name='update'),
    path('logger/<int:pk>/edit_note', logger.EditNoteView.as_view(), name='edit_note'),
    path('logger/<int:pk>/delete', logger.DeleteView.as_view(), name='delete'),
    path('logger/<int:pk>/monitor/<int:period>', logger.MonitorView.as_view(), name='monitor'),
    path('logger/<int:pk>/grab', logger.GrabView.as_view(), name='grab'),
    # API
    path('api/<int:pk>/add', logger.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', logger.ListAPIView.as_view(), name='api_list'),
    path('api/logger/<int:pk>', logger.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/logger/<int:pk>/update', logger.UpdateAPIView.as_view(), name='api_update'),
    path('api/logger/<int:pk>/delete', logger.DeleteAPIView.as_view(), name='api_delete')
]

from django.urls import path
from .views import calendars, plan

app_name = 'calendars'
urlpatterns = [
    path('<int:pk>/add', calendars.AddView.as_view(), name='add'),
    path('<int:pk>/import', calendars.ImportView.as_view(), name='import'),
    path('<int:pk>/clone', calendars.CloneView.as_view(), name='clone'),
    path('<int:pk>/list', calendars.ListView.as_view(), name='list'),
    path('calendar/<int:pk>/<int:year>/<int:month>', calendars.DetailView.as_view(), name='detail'),
    path('calendar/<int:pk>/<int:year>/<int:month>/<int:day>/detail', calendars.DayDetailView.as_view(), name='day_detail'),
    path('calendar/<int:pk>/<int:year>/<int:month>/<int:day>/chart', calendars.DayChartView.as_view(), name='day_chart'),
    path('calendar/<int:pk>/update', calendars.UpdateView.as_view(), name='update'),
    path('calendar/<int:pk>/delete', calendars.DeleteView.as_view(), name='delete'),
    path('calendar/<int:pk>/edit_note', calendars.EditNoteView.as_view(), name='edit_note'),
    path('calendar/<int:pk>/token/<int:ind>', calendars.TokenView.as_view(), name='token'),
    path('calendar/<int:pk>/pull', calendars.PullView.as_view(), name='pull'),
    path('calendar/<int:pk>/push', calendars.PushView.as_view(), name='push'),
    path('calendar/<int:pk>/log', calendars.LogView.as_view(), name='log'),
    path('calendar/<int:pk>/set_remote', calendars.SetRemoteView.as_view(), name='set_remote'),
    path('calendar/<int:pk>/clear_remote', calendars.ClearRemoteView.as_view(), name='clear_remote'),
    # API
    path('api/<int:pk>/add', calendars.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', calendars.ListAPIView.as_view(), name='api_list'),
    path('api/calendar/<int:pk>', calendars.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/calendar/<int:pk>/update', calendars.UpdateAPIView.as_view(), name='api_update'),
    # Plan
    path('calendar/<int:pk>/plan/add/<int:year>/<int:month>/<int:day>', plan.AddView.as_view(), name='plan_add'),
    path('plan/<int:pk>/update', plan.UpdateView.as_view(), name='plan_update'),
    path('plan/<int:pk>/delete', plan.DeleteView.as_view(), name='plan_delete'),
    # Plan API
    path('api/calendar/<int:pk>/plan/add', plan.AddAPIView.as_view(), name='api_plan_add'),
    path('api/calendar/<int:pk>/plan/list', plan.ListAPIView.as_view(), name='api_plan_list'),
    path('api/plan/<int:pk>', plan.RetrieveAPIView.as_view(), name='api_plan_retrieve'),
    path('api/plan/<int:pk>/update', plan.UpdateAPIView.as_view(), name='api_plan_update'),
    path('api/plan/<int:pk>/delete', plan.DeleteAPIView.as_view(), name='api_plan_delete')
]

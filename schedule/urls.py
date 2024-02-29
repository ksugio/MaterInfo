from django.urls import path
from .views import schedule, plan

app_name = 'schedule'
urlpatterns = [
    # Schedule
    path('<int:pk>/add', schedule.AddView.as_view(), name='add'),
    path('<int:pk>/import', schedule.ImportView.as_view(), name='import'),
    path('<int:pk>/clone', schedule.CloneView.as_view(), name='clone'),
    path('<int:pk>/list', schedule.ListView.as_view(), name='list'),
    path('schedule/<int:pk>', schedule.DetailView.as_view(), name='detail'),
    path('schedule/<int:pk>/update', schedule.UpdateView.as_view(), name='update'),
    path('schedule/<int:pk>/delete', schedule.DeleteView.as_view(), name='delete'),
    path('schedule/<int:pk>/chart', schedule.ChartView.as_view(), name='chart'),
    path('schedule/<int:pk>/token/<int:ind>', schedule.TokenView.as_view(), name='token'),
    path('schedule/<int:pk>/pull', schedule.PullView.as_view(), name='pull'),
    path('schedule/<int:pk>/push', schedule.PushView.as_view(), name='push'),
    path('schedule/<int:pk>/set_remote', schedule.SetRemoteView.as_view(), name='set_remote'),
    path('schedule/<int:pk>/clear_remote', schedule.ClearRemoteView.as_view(), name='clear_remote'),
    #  Schedule API
    path('api/<int:pk>/add', schedule.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', schedule.ListAPIView.as_view(), name='api_list'),
    path('api/schedule/<int:pk>', schedule.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/schedule/<int:pk>/update', schedule.UpdateAPIView.as_view(), name='api_update'),
    path('api/schedule/<int:pk>/delete', schedule.DeleteAPIView.as_view(), name='api_delete'),
    # Plan
    path('schedule/<int:pk>/plan/add', plan.AddView.as_view(), name='plan_add'),
    path('plan/<int:pk>/update', plan.UpdateView.as_view(), name='plan_update'),
    path('plan/<int:pk>/delete', plan.DeleteView.as_view(), name='plan_delete'),
    # Plan API
    path('api/schedule/<int:pk>/plan/add', plan.AddAPIView.as_view(), name='api_plan_add'),
    path('api/schedule/<int:pk>/plan/list', plan.ListAPIView.as_view(), name='api_plan_list'),
    path('api/plan/<int:pk>', plan.RetrieveAPIView.as_view(), name='api_plan_retrieve'),
    path('api/plan/<int:pk>/update', plan.UpdateAPIView.as_view(), name='api_plan_update'),
    path('api/plan/<int:pk>/delete', plan.DeleteAPIView.as_view(), name='api_plan_delete')
]

from django.urls import include, path
from editor.views.blocks.schedule import *


app_name = 'schedule'
urlpatterns = [
    path('create/', ScheduleBlockCreateView.as_view(extra_context={'expanded': True, 'type': app_name}), name='create'),
    path('<int:pk>/update/', ScheduleBlockUpdateView.as_view(extra_context={'expanded': True}), name='update'),
    path('<int:block_id>/schedule/<int:pk>/update/properties/',
         SchedulePropertiesUpdateView.as_view(extra_context={'expanded': False}), name='update_properties'),
    path('<int:block_id>/schedule/<int:schedule_id>/override/', include('editor.urls.blocks.schedule.override')),
    path('<int:block_id>/schedule/<int:schedule_id>/topic/', include('editor.urls.blocks.schedule.topic')),
    path('<int:block_id>/schedule/<int:schedule_id>/unit/', include('editor.urls.blocks.schedule.unit')),
]

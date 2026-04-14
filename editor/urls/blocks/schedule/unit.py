from django.urls import path
from editor.views.blocks.schedule.unit import *


app_name = 'unit'
urlpatterns = [
    path('create/', ScheduleUnitCreateView.as_view(), name='create'),
    path('<int:pk>/delete/', ScheduleUnitDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', ScheduleUnitUpdateView.as_view(), name='update'),
]

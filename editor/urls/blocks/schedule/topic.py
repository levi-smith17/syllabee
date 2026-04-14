from django.urls import path
from editor.views.blocks.schedule.topic import *


app_name = 'topic'
urlpatterns = [
    path('create/', ScheduleTopicCreateView.as_view(), name='create'),
    path('<int:pk>/copy/', ScheduleTopicCopyView.as_view(), name='copy'),
    path('<int:pk>/delete/', ScheduleTopicDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', ScheduleTopicUpdateView.as_view(), name='update'),
]

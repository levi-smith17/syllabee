from django.urls import path
from editor.views.blocks.schedule.override import *


app_name = 'override'
urlpatterns = [
    path('create/', OverrideCreateView.as_view(), name='create'),
    path('<int:pk>/delete/', OverrideDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', OverrideUpdateView.as_view(), name='update'),
]

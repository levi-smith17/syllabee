from django.urls import path
from editor.views.blocks.video import *


app_name = 'video'
urlpatterns = [
    path('create/', VideoBlockCreateView.as_view(extra_context={'expanded': False, 'type': app_name}), name='create'),
    path('<int:pk>/update/', VideoBlockUpdateView.as_view(extra_context={'expanded': False}), name='update'),
]

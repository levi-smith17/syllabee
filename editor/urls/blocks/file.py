from django.urls import path
from editor.views.blocks.file import *


app_name = 'file'
urlpatterns = [
    path('create/', FileBlockCreateView.as_view(extra_context={'expanded': False, 'type': app_name}), name='create'),
    path('<int:pk>/update/', FileBlockUpdateView.as_view(extra_context={'expanded': False}), name='update'),
]

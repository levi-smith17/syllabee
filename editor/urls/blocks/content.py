from django.urls import path
from editor.views.blocks.content import *


app_name = 'content'
urlpatterns = [
    path('create/', ContentBlockCreateView.as_view(extra_context={'expanded': True, 'type': app_name}), name='create'),
    path('<int:pk>/update/', ContentBlockUpdateView.as_view(extra_context={'expanded': True}), name='update'),
]

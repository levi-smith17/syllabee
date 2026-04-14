from django.urls import path
from editor.views.blocks.grade_determination import *


app_name = 'grade_determination'
urlpatterns = [
    path('create/', GradeDeterminationBlockCreateView.as_view(extra_context={'expanded': False, 'type': app_name}),
         name='create'),
    path('<int:pk>/update/', GradeDeterminationBlockUpdateView.as_view(extra_context={'expanded': False}),
         name='update'),
]

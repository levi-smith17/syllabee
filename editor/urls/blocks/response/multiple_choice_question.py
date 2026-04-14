from django.urls import path
from editor.views.blocks.response.multiple_choice_question import *


app_name = 'multiple_choice_question'
urlpatterns = [
    path('create/', MultipleChoiceQuestionCreateView.as_view(extra_context={'type': app_name}), name='create'),
    path('<int:pk>/delete/', MultipleChoiceQuestionDeleteView.as_view(), name='delete'),
    path('<int:pk>/response/', MultipleChoiceQuestionUpdateView.as_view(), name='response'),
    path('<int:pk>/update/', MultipleChoiceQuestionUpdateView.as_view(), name='update'),
]

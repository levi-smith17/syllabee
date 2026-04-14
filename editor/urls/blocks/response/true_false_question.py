from django.urls import path
from editor.views.blocks.response.true_false_question import *


app_name = 'true_false_question'
urlpatterns = [
    path('create/', TrueFalseQuestionCreateView.as_view(extra_context={'type': app_name}), name='create'),
    path('<int:pk>/delete/', TrueFalseQuestionDeleteView.as_view(), name='delete'),
    path('<int:pk>/response/', TrueFalseQuestionUpdateView.as_view(), name='response'),
    path('<int:pk>/update/', TrueFalseQuestionUpdateView.as_view(), name='update'),
]

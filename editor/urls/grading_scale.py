from django.urls import path
from editor.views.grading_scale import *


app_name = 'gradingscale'
urlpatterns = [
    path('', GradingScaleListView.as_view(), name='list'),
    path('create/', GradingScaleCreateView.as_view(), name='create'),
    path('<int:pk>/delete/', GradingScaleDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', GradingScaleUpdateView.as_view(), name='update'),
]

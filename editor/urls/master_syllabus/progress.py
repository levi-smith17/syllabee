from django.urls import path
from editor.views.progress import *


app_name = 'progress'
urlpatterns = [
    path('', ProgressDashboardView.as_view(), name='dashboard'),
    path('<int:pk>/', ProgressDetailView.as_view(), name='detail'),
    path('<str:section_hash>/student/<int:student_id>/reset/', ProgressResetView.as_view(), name='reset'),
    path('attempts/<int:response_progress_id>/', ProgressAttemptDetailView.as_view(), name='attempts'),
    path('details/<int:section_progress_id>/', ProgressStudentDetailView.as_view(), name='details'),
]

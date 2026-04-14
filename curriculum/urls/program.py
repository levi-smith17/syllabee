from django.urls import include, path
from curriculum.views.program import *


app_name = 'program'
urlpatterns = [
    path('create/', ProgramCreateView.as_view(), name='create'),
    path('list/', ProgramListView.as_view(), name='list'),
    path('<int:pk>/', ProgramDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', ProgramDeleteView.as_view(), name='delete'),
    path('<int:pk>/print/', ProgramPrintView.as_view(), name='print'),
    path('<int:pk>/update/', ProgramUpdateView.as_view(), name='update'),
    path('<int:program_id>/term/', include('curriculum.urls.term')),
]

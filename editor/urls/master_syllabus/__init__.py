from django.urls import include, path
from editor.views.master_syllabus import *


app_name = 'mastersyllabus'
urlpatterns = [
    path('create/', MasterSyllabusCreateView.as_view(), name='create'),
    path('list/', MasterSyllabusListView.as_view(), name='list'),
    path('<int:pk>/delete/', MasterSyllabusDeleteView.as_view(), name='delete'),
    path('<int:pk>/interactive/', MasterSyllabusInteractiveView.as_view(), name='interactive'),
    path('<int:pk>/lock/', MasterSyllabusLockView.as_view(), name='lock'),
    path('<int:pk>/toc/', MasterSyllabusTocView.as_view(extra_context={'tab': 'segments'}), name='toc'),
    path('<int:pk>/message/<int:message_id>/toc/', MasterSyllabusTocView.as_view(extra_context={'tab': 'messages'}),
         name='toc_message'),
    path('<int:pk>/segment/<int:segment_id>/toc/', MasterSyllabusTocView.as_view(extra_context={'tab': 'segments'}),
         name='toc_segment'),
    path('<int:pk>/update/', MasterSyllabusUpdateView.as_view(), name='update'),
    path('<int:master_syllabus_id>/message/', include('editor.urls.master_syllabus.message')),
    path('<int:master_syllabus_id>/progress/', include('editor.urls.master_syllabus.progress')),
    path('<int:master_syllabus_id>/segment/', include('editor.urls.master_syllabus.segment')),
]

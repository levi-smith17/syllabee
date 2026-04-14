from django.urls import path
from editor.views.blocks.course_syllabus import *


app_name = 'course_syllabus'
urlpatterns = [
    path('<int:pk>/update/', CourseSyllabusBlockUpdateView.as_view(extra_context={'expanded': False}), name='update'),
]

from django.urls import include, path
from editor.views.registration.course_requisite_block import *


app_name = 'block'
urlpatterns = [
    path('create/', CourseRequisiteBlockCreateView.as_view(), name='create'),
    path('detail/', CourseRequisiteBlockDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', CourseRequisiteBlockDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', CourseRequisiteBlockUpdateView.as_view(), name='update'),
    path('<int:block_id>/requisite/', include('editor.urls.registration.course.requisite')),
]

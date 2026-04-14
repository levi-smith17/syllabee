from django.urls import include, path
from curriculum.views.course import *


app_name = 'course'
urlpatterns = [
    path('create/', CourseCreateView.as_view(), name='create'),
    path('<int:pk>/delete/', CourseDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', CourseUpdateView.as_view(), name='update'),
    path('<int:course_id>/extension/', include('curriculum.urls.course.extension'))
]

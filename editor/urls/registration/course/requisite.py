from django.urls import path
from editor.views.registration.course_requisite import *


app_name = 'requisite'
urlpatterns = [
    path('create/', CourseRequisiteCreateView.as_view(), name='create'),
    path('<int:pk>/delete/', CourseRequisiteDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', CourseRequisiteUpdateView.as_view(), name='update'),
]

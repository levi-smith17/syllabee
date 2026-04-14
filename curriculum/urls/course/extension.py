from django.urls import path
from curriculum.views.course.extension import *


app_name = 'extension'
urlpatterns = [
    path('create/', CourseExtensionCreateView.as_view(), name='create'),
    path('detail/', CourseExtensionDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', CourseExtensionDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', CourseExtensionUpdateView.as_view(), name='update'),
]

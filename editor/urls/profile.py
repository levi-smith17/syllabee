from django.urls import path
from editor.views.profile import *


app_name = 'profile'
urlpatterns = [
    path('<int:pk>/', ProfileDetailView.as_view(), name='detail'),
    path('<int:pk>/master_syllabus/<int:master_syllabus_id>/', ProfileDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', ProfileUpdateView.as_view(), name='update'),
]

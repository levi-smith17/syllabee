from django.urls import path
from editor.views.message import *


app_name = 'message'
urlpatterns = [
    path('', MessageDetailView.as_view(), name='detail'),
    path('create/', MessageCreateView.as_view(), name='create'),
    path('<int:pk>/', MessageDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', MessageDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', MessageUpdateView.as_view(), name='update'),
]

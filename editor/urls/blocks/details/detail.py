from django.urls import path
from editor.views.blocks.details.detail import *


app_name = 'detail'
urlpatterns = [
    path('arrange/', DetailsBlockDetailArrangeView.as_view(), name='arrange'),
    path('create/', DetailsBlockDetailCreateView.as_view(), name='create'),
    path('<int:pk>/delete/', DetailsBlockDetailDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', DetailsBlockDetailUpdateView.as_view(), name='update'),
]

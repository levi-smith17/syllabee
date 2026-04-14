from django.urls import path
from editor.views.blocks.listing.item import *


app_name = 'item'
urlpatterns = [
    path('arrange/', ListBlockItemArrangeView.as_view(), name='arrange'),
    path('create/', ListBlockItemCreateView.as_view(), name='create'),
    path('<int:pk>/delete/', ListBlockItemDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', ListBlockItemUpdateView.as_view(), name='update'),
]

from django.urls import path
from editor.views.blocks.table.row import *


app_name = 'row'
urlpatterns = [
    path('create/', TableBlockRowCreateView.as_view(), name='create'),
    path('<int:pk>/delete/', TableBlockRowDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', TableBlockRowUpdateView.as_view(), name='update'),
]

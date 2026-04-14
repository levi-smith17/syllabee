from django.urls import path
from editor.views.blocks.table.column import *


app_name = 'column'
urlpatterns = [
    path('<int:pk>/update/', TableBlockColumnUpdateView.as_view(), name='update'),
]

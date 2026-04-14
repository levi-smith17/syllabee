from django.urls import path
from editor.views.quick_link import *


app_name = 'quicklink'
urlpatterns = [
    path('', QuickLinkListView.as_view(), name='list'),
    path('create/', QuickLinkCreateView.as_view(), name='create'),
    path('<int:pk>/delete/', QuickLinkDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', QuickLinkUpdateView.as_view(), name='update'),
]

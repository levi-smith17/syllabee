from django.urls import path
from editor.views.registration.term import *


app_name = 'term'
urlpatterns = [
    path('', TermListView.as_view(), name='list'),
    path('create/', TermCreateView.as_view(), name='create'),
    path('detail/', TermDetailView.as_view(), name='detail'),
    path('search/', TermSearchView.as_view(), name='search'),
    path('search/<str:pagination>/', TermListView.as_view(), name='pagination'),
    path('<int:pk>/archive/', TermArchiveView.as_view(), name='archive'),
    path('<int:pk>/delete/', TermDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', TermUpdateView.as_view(), name='update'),
]

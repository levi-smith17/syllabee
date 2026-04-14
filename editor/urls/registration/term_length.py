from django.urls import path
from editor.views.registration.term_length import *


app_name = 'termlength'
urlpatterns = [
    path('', TermLengthListView.as_view(), name='list'),
    path('create/', TermLengthCreateView.as_view(), name='create'),
    path('detail/', TermLengthDetailView.as_view(), name='detail'),
    path('search/', TermLengthSearchView.as_view(), name='search'),
    path('search/<str:pagination>/', TermLengthListView.as_view(), name='pagination'),
    path('<int:pk>/delete/', TermLengthDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', TermLengthUpdateView.as_view(), name='update'),
]

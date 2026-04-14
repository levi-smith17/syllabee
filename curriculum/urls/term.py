from django.urls import include, path
from curriculum.views.term import *


app_name = 'term'
urlpatterns = [
    path('create/', TermCreateView.as_view(), name='create'),
    path('<int:pk>/delete/', TermDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', TermUpdateView.as_view(), name='update'),
    path('<int:term_id>/course/', include('curriculum.urls.course')),
]

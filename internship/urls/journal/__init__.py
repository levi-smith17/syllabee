from django.urls import include, path
from internship.views.internship import *


app_name = 'journal'
urlpatterns = [
    path('create/', InternshipCreateView.as_view(), name='create'),
    path('detail/', InternshipDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', InternshipDeleteView.as_view(), name='delete'),
    path('<int:pk>/detail/', InternshipDetailView.as_view(), name='detail'),
    path('<int:pk>/download/', InternshipDownloadView.as_view(), name='download'),
    path('<int:pk>/print/', InternshipPrintView.as_view(), name='print'),
    path('<int:pk>/update/', InternshipUpdateView.as_view(), name='update'),
    path('<int:internship_id>/location/', include('internship.urls.journal.location'))
]

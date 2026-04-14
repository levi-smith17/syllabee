from django.urls import include, path
from internship.views.location import *


app_name = 'location'
urlpatterns = [
    path('create/', InternshipLocationCreateView.as_view(), name='create'),
    path('<int:pk>/delete/', InternshipLocationDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', InternshipLocationUpdateView.as_view(), name='update'),
    path('<int:pk>/validate/', InternshipLocationValidationView.as_view(), name='validate'),
    path('<int:pk>/verify/', InternshipJournalEntryVerifyAllView.as_view(), name='verify'),
    path('<int:location_id>/entry/', include('internship.urls.journal.location.entry'))
]

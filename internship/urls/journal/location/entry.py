from django.urls import path
from internship.views.entry import *


app_name = 'entry'
urlpatterns = [
    path('create/', InternshipJournalEntryCreateView.as_view(), name='create'),
    path('<int:pk>/delete/', InternshipJournalEntryDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', InternshipJournalEntryUpdateView.as_view(), name='update'),
    path('<int:pk>/verify/', InternshipJournalEntryVerifyView.as_view(), name='verify'),
]

from django.urls import include, path
from internship.views import *


app_name = 'internship'
urlpatterns = [
    path('', InternshipIndexView.as_view(), name='index'),
    path('toc/', InternshipTocView.as_view(), name='toc'),
    path('journal/', include('internship.urls.journal')),
]

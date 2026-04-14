from django.urls import include, path
from curriculum.views.curriculum import *


app_name = 'curriculum'
urlpatterns = [
    path('', CurriculumIndexView.as_view(), name='index'),
    path('content/', CurriculumContentView.as_view(), name='content'),
    path('program/', include('curriculum.urls.program')),
    path('toc/', CurriculumTocView.as_view(), name='toc'),
]

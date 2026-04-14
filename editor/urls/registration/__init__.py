from django.urls import include, path
from editor.views.registration import *

app_name = 'registration'
urlpatterns = [
    path('', RegistrationIndexView.as_view(), name='index'),
    path('course/', include('editor.urls.registration.course')),
    path('course_ratio/', include('editor.urls.registration.course_ratio')),
    path('section/', include('editor.urls.registration.section')),
    path('term/', include('editor.urls.registration.term')),
    path('term_length/', include('editor.urls.registration.term_length')),
    path('toc/<str:model>/', RegistrationTocView.as_view(), name='toc'),
]

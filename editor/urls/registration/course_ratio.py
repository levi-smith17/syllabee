from django.urls import path
from editor.views.registration.course_ratio import *


app_name = 'courseratio'
urlpatterns = [
    path('', CourseRatioListView.as_view(), name='list'),
    path('create/', CourseRatioCreateView.as_view(), name='create'),
    path('detail/', CourseRatioDetailView.as_view(), name='detail'),
    path('search/', CourseRatioSearchView.as_view(), name='search'),
    path('search/filter/clear/<str:filter_key>/', CourseRatioListView.as_view(), name='filter_clear'),
    path('search/<str:pagination>/', CourseRatioListView.as_view(), name='pagination'),
    path('<int:pk>/delete/', CourseRatioDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', CourseRatioUpdateView.as_view(), name='update'),
]

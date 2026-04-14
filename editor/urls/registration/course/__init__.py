from django.urls import include, path
from editor.views.registration.course import *


app_name = 'course'
urlpatterns = [
    path('', CourseListView.as_view(), name='list'),
    path('create/', CourseCreateView.as_view(), name='create'),
    path('detail/', CourseDetailView.as_view(), name='detail'),
    path('search/', CourseSearchView.as_view(), name='search'),
    path('search/filter/', CourseFilterView.as_view(), name='filter'),
    path('search/filter/clear/<str:filter_key>/', CourseListView.as_view(), name='filter_clear'),
    path('search/<str:pagination>/', CourseListView.as_view(), name='pagination'),
    path('<int:pk>/delete/', CourseDeleteView.as_view(), name='delete'),
    path('<int:pk>/rename/<int:program_id>/', CourseRenameView.as_view(), name='rename'),
    path('<int:pk>/update/', CourseUpdateView.as_view(), name='update'),
    path('<int:course_id>/block/', include('editor.urls.registration.course.requisite_block')),
]

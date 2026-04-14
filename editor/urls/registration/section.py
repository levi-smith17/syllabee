from django.urls import path
from editor.views.registration.section import *


app_name = 'section'
urlpatterns = [
    path('', SectionListView.as_view(), name='list'),
    path('create/', SectionCreateView.as_view(), name='create'),
    path('detail/', SectionDetailView.as_view(), name='detail'),
    path('search/', SectionSearchView.as_view(), name='search'),
    path('search/filter/', SectionFilterView.as_view(), name='filter'),
    path('search/filter/clear/<str:filter_key>/', SectionListView.as_view(), name='filter_clear'),
    path('search/<str:pagination>/', SectionListView.as_view(), name='pagination'),
    path('<int:pk>/delete/', SectionDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', SectionUpdateView.as_view(), name='update'),
]

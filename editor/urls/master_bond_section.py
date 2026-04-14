from django.urls import path
from editor.views.master_bond_section import *


app_name = 'masterbondsection'
urlpatterns = [
    path('filter/', MasterBondSectionFilterView.as_view(), name='filter'),
    path('filter/clear/<str:filter_key>/', MasterBondSectionListView.as_view(), name='filter_clear'),
]

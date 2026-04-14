from django.urls import path
from editor.views.master_bond import *
from editor.views.master_bond_section import MasterBondSectionUpdateView
from editor.views.funcs import copy_masterbond_content


app_name = 'masterbond'
urlpatterns = [
    path('arrange/', MasterBondArrangeView.as_view(), name='arrange'),
    path('create/', MasterBondCreateView.as_view(), name='create'),
    path('create/submit/', copy_masterbond_content, name='create_submit'),
    path('search/', MasterBondSearchView.as_view(), name='search'),
    path('list/', MasterBondListView.as_view(), name='list'),
    path('<int:pk>/delete/', MasterBondDeleteView.as_view(), name='delete'),
    path('<int:master_bond_id>/sections/', MasterBondSectionUpdateView.as_view(), name='sections'),
    path('<int:pk>/visibility/', MasterBondVisibilityView.as_view(), name='visibility'),
]

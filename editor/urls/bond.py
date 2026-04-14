from django.urls import path
from editor.views.bond import *
from editor.views.funcs import copy_bond_content


app_name = 'bond'
urlpatterns = [
    path('arrange/', BondArrangeView.as_view(), name='arrange'),
    path('create/', BondCreateView.as_view(), name='create'),
    path('create/submit/', copy_bond_content, name='create_submit'),
    path('create/block/<int:pk>/', BondDetailView.as_view(), name='create_block'),
    path('create/block/<int:block_id>/associations/', BondListView.as_view(), name='create_block_links'),
    path('search/', BondSearchView.as_view(), name='search'),
    path('<int:pk>/delete/', BondDeleteView.as_view(), name='delete'),
]

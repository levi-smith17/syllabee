from django.urls import include, path
from editor.views.blocks.table.block import *


app_name = 'table'
urlpatterns = [
    path('create/', TableBlockCreateView.as_view(extra_context={'expanded': True, 'type': app_name}), name='create'),
    path('<int:pk>/update/', TableBlockUpdateView.as_view(extra_context={'expanded': True}), name='update'),
    path('<int:pk>/update/properties/', TableBlockPropertiesUpdateView.as_view(extra_context={'expanded': False}),
         name='update_properties'),
    path('<int:block_id>/col/', include('editor.urls.blocks.table.column')),
    path('<int:block_id>/row/', include('editor.urls.blocks.table.row')),
]

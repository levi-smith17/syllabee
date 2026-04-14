from django.urls import include, path
from editor.views.blocks.listing import *


app_name = 'list'
urlpatterns = [
    path('create/', ListBlockCreateView.as_view(extra_context={'expanded': True, 'type': app_name}), name='create'),
    path('<int:pk>/update/', ListBlockUpdateView.as_view(extra_context={'expanded': True}), name='update'),
    path('<int:pk>/update/properties/', ListBlockPropertiesUpdateView.as_view(extra_context={'expanded': False}),
         name='update_properties'),
    path('<int:block_id>/item/', include('editor.urls.blocks.listing.item')),
]

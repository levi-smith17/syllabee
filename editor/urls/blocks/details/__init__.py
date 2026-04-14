from django.urls import include, path
from editor.views.blocks.details.block import *


app_name = 'details'
urlpatterns = [
    path('create/', DetailsBlockCreateView.as_view(extra_context={'expanded': True, 'type': app_name}), name='create'),
    path('<int:pk>/update/', DetailsBlockUpdateView.as_view(extra_context={'expanded': True}), name='update'),
    path('<int:block_id>/detail/', include('editor.urls.blocks.details.detail')),
]

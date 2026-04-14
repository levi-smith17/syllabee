from django.urls import include, path
from editor.views.block import *
from editor.views.funcs import batch_block_edit


app_name = 'block'
urlpatterns = [
    path('', include('editor.urls.blocks')),
    path('<int:pk>/delete/', BlockDeleteView.as_view(), name='delete'),
    path('<int:pk>/publish/', PrintableBlockPublishView.as_view(), name='publish'),
    path('<int:pk>/update/', BlockDetailView.as_view(extra_context={'expanded': True}), name='detail'),
    path('edit/batch/', BlockBatchView.as_view(), name='update_batch'),
    path('edit/batch/submit/', batch_block_edit, name='update_batch_submit'),
]

from django.urls import path
from editor.views.segment import *
from editor.views.funcs import batch_segment_edit


app_name = 'segment'
urlpatterns = [
    path('', SegmentDetailView.as_view(), name='detail'),
    path('create/<int:order>/', SegmentCreateView.as_view(), name='create'),
    path('edit/batch/', SegmentBatchView.as_view(), name='update_batch'),
    path('edit/batch/submit/', batch_segment_edit, name='update_batch_submit'),
    path('<int:pk>/', SegmentDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', SegmentDeleteView.as_view(), name='delete'),
    path('<int:pk>/preview/', SegmentDetailPreview.as_view(), name='preview'),
    path('<int:pk>/update/', SegmentUpdateView.as_view(), name='update'),
]

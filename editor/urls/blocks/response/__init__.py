from django.urls import include, path
from editor.views.blocks.response import *


app_name = 'response'
urlpatterns = [
    path('create/', ResponseBlockCreateView.as_view(extra_context={'expanded': True, 'type': app_name}), name='create'),
    path('<int:pk>/list/', ResponseBlockListView.as_view(), name='list'),
    path('<int:pk>/update/', ResponseBlockUpdateView.as_view(extra_context={'expanded': True}), name='update'),
    path('<int:pk>/update/properties/', ResponseBlockPropertiesUpdateView.as_view(extra_context={'expanded': False}),
         name='update_properties'),
    path('<int:block_id>/multiple_choice_question/', include('editor.urls.blocks.response.multiple_choice_question')),
    path('<int:block_id>/true_false_question/', include('editor.urls.blocks.response.true_false_question')),
]

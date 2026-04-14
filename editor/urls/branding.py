from django.urls import path
from editor.views.branding import *


app_name = 'branding'
urlpatterns = [
    path('<int:pk>/update/', BrandingUpdateView.as_view(), name='update'),
]

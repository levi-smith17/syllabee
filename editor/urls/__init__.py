from django.urls import include, path
from editor.views.master_syllabus import MasterSyllabusIndexView


app_name = 'editor'
urlpatterns = [
    path('', MasterSyllabusIndexView.as_view(), name='index'),
    path('branding/', include('editor.urls.branding')),
    path('grading_scale/', include('editor.urls.grading_scale')),
    path('master_bond_section/', include('editor.urls.master_bond_section')),
    path('master_syllabus/', include('editor.urls.master_syllabus')),
    path('master_syllabus/<int:master_syllabus_id>/master_bond/', include('editor.urls.master_bond')),
    path('master_syllabus/<int:master_syllabus_id>/segment/<int:segment_id>/block/', include('editor.urls.block')),
    path('master_syllabus/<int:master_syllabus_id>/segment/<int:segment_id>/bond/', include('editor.urls.bond')),
    path('profile/', include('editor.urls.profile')),
    path('quicklinks/', include('editor.urls.quick_link')),
    path('registration/', include('editor.urls.registration')),
]

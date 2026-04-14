from django.urls import include, path


urlpatterns = [
    path('content/', include('editor.urls.blocks.content')),
    path('course_syllabus/', include('editor.urls.blocks.course_syllabus')),
    path('details/', include('editor.urls.blocks.details')),
    path('file/', include('editor.urls.blocks.file')),
    path('grade_determination/', include('editor.urls.blocks.grade_determination')),
    path('listing/', include('editor.urls.blocks.listing')),
    path('response/', include('editor.urls.blocks.response')),
    path('schedule/', include('editor.urls.blocks.schedule')),
    path('table/', include('editor.urls.blocks.table')),
    path('video/', include('editor.urls.blocks.video')),
]

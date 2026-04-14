"""syllabee URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from core.views import funcs
from core.views.core import ApplicationLaunchView, LtiDeepLinkView
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from decouple import config
from lti_tool.views import jwks, OIDCLoginInitView

SECRET_ADMIN_URL = config('SECRET_ADMIN_URL')
urlpatterns = [
    path(f'admin_{SECRET_ADMIN_URL}/', admin.site.urls),
    path('curriculum/', include('curriculum.urls')),
    path('editor/', include('editor.urls')),
    path('internship/', include('internship.urls')),
    path('microsoft/', include('microsoft_authentication.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('signin/', auth_views.LoginView.as_view(template_name='core/helpers/login.html',
                                                 extra_context=funcs.get_environs_branding()),
         name='signin'),
    path('signout/', auth_views.LogoutView.as_view(), name='signout'),
    path('', include('viewer.urls')),
    path('', include('core.urls')),
    path('.well-known/jwks.json', jwks, name='jwks'),
    #path('jwks.json', jwks, name='jwks'),
    path('init/<uuid:registration_uuid>/', OIDCLoginInitView.as_view(), name='init'),
    path('lti/', ApplicationLaunchView.as_view(), name='lti'),
    path('lti_deep_link/', LtiDeepLinkView.as_view(), name='lti_deep_link'),
]

handler400 = funcs.handler400
handler403 = funcs.handler403
handler404 = funcs.handler404
handler500 = funcs.handler500

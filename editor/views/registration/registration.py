from ...models import *
from core.views.funcs import get_environs, get_loader_context, get_model, reset_pagination
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView, View
from django.views.generic.base import ContextMixin


class RegistrationContextMixin(PermissionRequiredMixin, ContextMixin, View):
    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        environs = get_model(self.request, model=CourseRatio, environs=environs)
        environs = get_model(self.request, model=Course, environs=environs)
        environs = get_model(self.request, model=Section, environs=environs)
        environs = get_model(self.request, model=Term, environs=environs)
        environs = get_model(self.request, model=TermLength, environs=environs)
        context = super().get_context_data(**kwargs)
        if 'model' in self.kwargs:
            context['model_to_autoload'] = self.kwargs['model']
        else:
            context['model_to_autoload'] = 'section'
        for model in environs['models']:
            reset_pagination(self.request, model['name'], False, True)
        context['master_syllabus'] = None
        context['visible'] = True
        return {**context, **environs}

    def has_permission(self):
        if self.request.user.has_perm('editor.add_course') or \
                self.request.user.has_perm('editor.change_course') or \
                self.request.user.has_perm('editor.delete_course') or \
                self.request.user.has_perm('editor.add_section') or \
                self.request.user.has_perm('editor.change_section') or \
                self.request.user.has_perm('editor.delete_section') or \
                self.request.user.has_perm('editor.add_term') or \
                self.request.user.has_perm('editor.change_term') or \
                self.request.user.has_perm('editor.delete_term') or \
                self.request.user.has_perm('editor.add_termlength') or \
                self.request.user.has_perm('editor.change_termlength') or \
                self.request.user.has_perm('editor.delete_termlength'):
            return True
        return False


class RegistrationIndexView(RegistrationContextMixin, TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['editable'] = True
        context['master_syllabus'] = None
        context['visible'] = True
        content_toc_json = '{"model": "' + context['model_to_autoload'] + '"}'
        context.update(get_loader_context(content=content_toc_json, profile='', toc=content_toc_json,
                                          title='Administration', view='admin', url=reverse('editor:registration:index')))
        return {**context, **environs}


class RegistrationTocView(RegistrationContextMixin, TemplateView):
    template_name = 'editor/registration/toc.html'

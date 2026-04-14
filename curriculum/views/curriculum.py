from ..models import Program
from core.views.funcs import (get_environs, get_loader_context)
from curriculum.views.program import ProgramContextMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView


class CurriculumContentView(PermissionRequiredMixin, ProgramContextMixin, TemplateView):
    permission_required = ('curriculum.view_program',)
    model = Program
    template_name = 'curriculum/content.html'


class CurriculumIndexView(PermissionRequiredMixin, TemplateView):
    permission_required = ('curriculum.view_program',)
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['editable'] = True
        if 'program_id' in self.request.session:
            content_toc_json = ('{"program_id": "' + str(self.request.session.get('program_id')) + '"}')
        else:
            content_toc_json = '{"program_id": "0"}'
        profile_json = ('{"instructor_id": "' + str(self.request.user.id) + '"}')
        context.update(get_loader_context(content=content_toc_json, profile=profile_json, toc=content_toc_json,
                                          title='Curriculum Builder', view='curriculum',
                                          url=reverse('curriculum:index')))
        return {**context, **environs}


class CurriculumTocView(PermissionRequiredMixin, TemplateView):
    permission_required = ('curriculum.view_program',)
    template_name = 'curriculum/toc.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['programs'] = Program.objects.filter(owner=self.request.user)
        context['program_id'] = self.request.session.get('program_id', 0)
        return {**context, **environs}

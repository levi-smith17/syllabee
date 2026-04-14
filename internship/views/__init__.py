from .entry import *
from .internship import *
from .location import *
from core.views import get_loader_context
from django.core.exceptions import PermissionDenied


class InternshipIndexView(PermissionRequiredMixin, TemplateView):
    permission_required = 'internship.view_internship'
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        if self.request.user.groups.filter(name__in=['admins', 'instructors']).exists():
            context = {'editable': True, 'internship_id': str(self.request.session.get('internship_id', 0))}
            content_json = ('{"internship_id": "' + str(self.request.session.get('internship_id', 0)) + '"}')
            profile_json = ('{"instructor_id": "' + str(self.request.user.id) + '"}')
            context.update(get_loader_context(content=content_json, profile=profile_json, title='Internship Management',
                                              view='internship', url=reverse('internship:index')))
        else:
            try:
                internship = Internship.objects.get(intern=self.request.user)
            except Internship.DoesNotExist:
                raise PermissionDenied('You are not currently enrolled in an internship. Please contact your instructor.')
            context = {'editable': False, 'internship_id': internship.id}
            content_json = ('{"internship_id": "' + str(internship.id) + '"}')
            profile_json = ('{"instructor_id": "' + str(internship.section.instructor.id) + '"}')
            context.update(get_loader_context(content=content_json, profile=profile_json, title='Internship Journal',
                                              view='internship', url=reverse('internship:index')))
        return {**context, **environs}


class InternshipTocView(PermissionRequiredMixin, TemplateView):
    permission_required = 'internship.view_internship'
    template_name = 'internship/toc.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        if self.request.user.groups.filter(name__in=['admins', 'instructors']).exists():
            context['internship_id'] = self.request.session.get('internship_id', 0)
            context['internships'] = Internship.objects.filter(section__instructor=self.request.user)
        return {**context, **environs}

from django.contrib.auth.mixins import AccessMixin
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.views.generic import View
from django.views.generic.base import ContextMixin
from editor.models import MasterBondSection
from editor.views.funcs import is_master_syllabus_archived, is_master_syllabus_locked


class MasterSyllabusLockedAccessMixin(AccessMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if 'master_syllabus_id' in kwargs:
            master_syllabus_id = kwargs['master_syllabus_id']
        elif 'pk' in kwargs:
            master_syllabus_id = kwargs['pk']
        else:
            master_syllabus_id = None
        if is_master_syllabus_archived(master_syllabus_id):
            self.permission_denied_message = 'This master syllabus is archived, so it cannot be modified.'
            return self.handle_no_permission()
        elif is_master_syllabus_locked(master_syllabus_id):
            self.permission_denied_message = 'This master syllabus is locked, so it cannot be modified.'
            return self.handle_no_permission()
        return super(MasterSyllabusLockedAccessMixin, self).dispatch(request, *args, **kwargs)


class MasterSyllabusTocContextMixin(ContextMixin, View):
    def get_success_url(self):
        try:
            return reverse('editor:mastersyllabus:toc_segment', args=(self.kwargs['master_syllabus_id'],
                                                         self.request.session.get('segment_id')))
        except NoReverseMatch:
            return reverse('editor:mastersyllabus:toc', args=(self.kwargs['master_syllabus_id'],))


class SectionRequiredAccessMixin(AccessMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        master_bond_section = (MasterBondSection.objects
                               .filter(master_bond__master_syllabus_id=self.kwargs['master_syllabus_id'],
                                       master_bond__segment_id=self.kwargs['segment_id'], section__isnull=False,
                                       owner=request.user)
                               .exists())
        if not master_bond_section:
            return self.handle_no_permission()
        else:
            return super(SectionRequiredAccessMixin, self).dispatch(request, *args, **kwargs)

    def get_permission_denied_message(self):
        self.permission_denied_message = 'This segment requires an associated section to complete the requested ' \
                                         'operation.'
        return self.permission_denied_message

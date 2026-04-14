from core.views import get_environs
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import ImproperlyConfigured
from django.views.generic.base import ContextMixin
from editor.models import MasterSyllabus, Profile
from internship.models import Internship, InternshipLocation, InternshipJournalEntry, InternshipSettings


class InternshipDownloadPrintContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        try:
            context['internship'] = Internship.objects.get(pk=self.kwargs['pk'])
            context['internship_settings'] = InternshipSettings.objects.get(coordinator=context['internship'].section.instructor)
            context['instructor'] = Profile.objects.get(pk=context['internship'].section.instructor.id)
            context['locations'] = InternshipLocation.objects.filter(internship=context['internship'])
            context['master_syllabus'] = MasterSyllabus.objects.filter(term__section=context['internship'].section)
        except (Internship.DoesNotExist, MasterSyllabus.DoesNotExist):
            raise ImproperlyConfigured('Unable to retrieve the print view for the requested internship.')
        return {**context, **environs}


class InternshipLocationAccessMixin(AccessMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        location = InternshipLocation.objects.get(pk=self.kwargs['pk'])
        if location.validated:
            return self.handle_no_permission()
        else:
            return super(InternshipLocationAccessMixin, self).dispatch(request, *args, **kwargs)

    def get_permission_denied_message(self):
        self.permission_denied_message = ('You cannot edit or delete a validated internship location. Please contact '
                                          'your instructor.')
        return self.permission_denied_message


class InternshipJournalEntryAccessMixin(AccessMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        entry = InternshipJournalEntry.objects.get(pk=self.kwargs['pk'])
        if entry.verified:
            return self.handle_no_permission()
        else:
            return super(InternshipJournalEntryAccessMixin, self).dispatch(request, *args, **kwargs)

    def get_permission_denied_message(self):
        self.permission_denied_message = ('You cannot edit or delete a verified journal entry. Please contact '
                                          'your instructor.')
        return self.permission_denied_message

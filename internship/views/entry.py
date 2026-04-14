from .funcs import update_completed_hours, update_grade
from .mixins import InternshipJournalEntryAccessMixin
from ..forms import InternshipJournalEntryForm, InternshipJournalEntryDeleteForm
from ..models import InternshipJournalEntry
from core.views.funcs import get_cbv_context, get_environs, get_modal
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView, View
from django.views.generic.base import ContextMixin


class InternshipJournalEntryContextMixin(ContextMixin, View):
    def get_success_url(self):
        return reverse('internship:journal:detail', args=(self.kwargs['internship_id'],))


class InternshipJournalEntryCreateView(PermissionRequiredMixin, FormInvalidMixin, InternshipJournalEntryContextMixin,
                                       CreateView):
    permission_required = ('internship.add_internshipjournalentry',)
    model = InternshipJournalEntry
    form_class = InternshipJournalEntryForm
    template_name = 'core/offcanvas/add.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('internship:journal:location:entry:create',
                                     args=(self.kwargs['internship_id'], self.kwargs['location_id'],))
        context['callback'] = 'done_load_regions'
        context['target'] = '#content-container'
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(InternshipJournalEntryCreateView, self).get_form_kwargs()
        kwargs.update({'location_id': self.kwargs['location_id']})
        return kwargs


class InternshipJournalEntryDeleteView(PermissionRequiredMixin, InternshipJournalEntryAccessMixin, FormInvalidMixin,
                                       DeleteViewFormMixin, InternshipJournalEntryContextMixin, DeleteView):
    permission_required = ('internship.delete_internshipjournalentry',)
    model = InternshipJournalEntry
    form_class = InternshipJournalEntryDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['callback'] = 'done_load_regions'
        context['modal']['target'] = '#content-container'
        context['modal']['url'] = reverse('internship:journal:location:entry:delete',
                                          args=(self.kwargs['internship_id'], self.kwargs['location_id'],
                                                self.kwargs['pk'],))
        return context


class InternshipJournalEntryUpdateView(PermissionRequiredMixin, InternshipJournalEntryAccessMixin, FormInvalidMixin,
                                       InternshipJournalEntryContextMixin, UpdateView):
    permission_required = ('internship.change_internshipjournalentry',)
    model = InternshipJournalEntry
    form_class = InternshipJournalEntryForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['callback'] = 'done_load_regions'
        context['delete_url'] = None
        context['edit_url'] = reverse('internship:journal:location:entry:update',
                                      args=(self.kwargs['internship_id'], self.kwargs['location_id'], self.object.id,))
        context['target'] = '#content-container'
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(InternshipJournalEntryUpdateView, self).get_form_kwargs()
        kwargs.update({'location_id': self.kwargs['location_id']})
        return kwargs


class InternshipJournalEntryVerifyView(PermissionRequiredMixin, FormInvalidMixin, InternshipJournalEntryContextMixin,
                                       UpdateView):
    permission_required = ('internship.change_internship',)
    model = InternshipJournalEntry
    form_class = InternshipJournalEntryDeleteForm
    template_name = 'editor/helpers/modal/generic.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        message = '<strong>WARNING</strong>: '
        if self.object.verified:
            message += ('unverifying this journal entry will allow the student to make changes to this entry. '
                        'Unverified journal entries do not count toward the student\'s total hours.')
        else:
            message += ('verifying this journal entry prevents the student from making changes to it. Verified journal '
                        'entries are counted toward the student\'s total hours.')
        context['modal'] = get_modal(message, message_alert_css='m-0', message_type='warning',
                                     operation=('unverified' if self.object.verified else 'verified'),
                                     target='#content-container',
                                     submit_icon=('journal-minus' if self.object.verified else 'journal-plus'),
                                     submit_text=('Unverify' if self.object.verified else 'Verify'),
                                     url=reverse('internship:journal:location:entry:verify',
                                                 args=(self.kwargs['internship_id'], self.kwargs['location_id'],
                                                       self.object.id,)))
        context['verbose_name'] = 'journal entry'
        return {**context, **environs}

    def form_valid(self, form):
        form.instance.verified = not bool(self.object.verified)
        self.object = form.save()
        update_completed_hours(self.request, self.kwargs['internship_id'])
        update_grade(self.request, self.kwargs['internship_id'])
        return super().form_valid(form)

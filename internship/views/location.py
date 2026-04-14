from .funcs import update_completed_hours, update_grade
from .mixins import InternshipLocationAccessMixin
from ..forms import InternshipLocationForm, InternshipLocationDeleteForm
from ..models import InternshipLocation, InternshipJournalEntry
from core.views.funcs import get_cbv_context, get_environs, get_modal
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView, View
from django.views.generic.base import ContextMixin


class InternshipLocationContextMixin(ContextMixin, View):
    def get_success_url(self):
        return reverse('internship:journal:detail', args=(self.kwargs['internship_id'],))


class InternshipLocationCreateView(PermissionRequiredMixin, FormInvalidMixin, InternshipLocationContextMixin,
                                   CreateView):
    permission_required = ('internship.add_internshiplocation',)
    model = InternshipLocation
    form_class = InternshipLocationForm
    template_name = 'core/offcanvas/add.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('internship:journal:location:create',
                                     args=(self.kwargs['internship_id'],))
        context['callback'] = 'done_load_regions'
        context['target'] = '#content-container'
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(InternshipLocationCreateView, self).get_form_kwargs()
        kwargs.update({'internship_id': self.kwargs['internship_id']})
        return kwargs


class InternshipLocationDeleteView(PermissionRequiredMixin, InternshipLocationAccessMixin, FormInvalidMixin,
                                   DeleteViewFormMixin, InternshipLocationContextMixin, DeleteView):
    permission_required = ('internship.delete_internshiplocation',)
    model = InternshipLocation
    form_class = InternshipLocationDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['callback'] = 'done_load_regions'
        context['modal']['target'] = '#content-container'
        context['modal']['url'] = reverse('internship:journal:location:delete',
                                          args=(self.kwargs['internship_id'], self.kwargs['pk'],))
        return context


class InternshipLocationUpdateView(PermissionRequiredMixin, InternshipLocationAccessMixin, FormInvalidMixin,
                                   InternshipLocationContextMixin, UpdateView):
    permission_required = ('internship.change_internshiplocation',)
    model = InternshipLocation
    form_class = InternshipLocationForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['callback'] = 'done_load_regions'
        context['delete_url'] = None
        context['edit_url'] = reverse('internship:journal:location:update',
                                      args=(self.kwargs['internship_id'], self.object.id,))
        context['target'] = '#content-container'
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(InternshipLocationUpdateView, self).get_form_kwargs()
        kwargs.update({'internship_id': self.kwargs['internship_id']})
        return kwargs


class InternshipLocationValidationView(PermissionRequiredMixin, FormInvalidMixin, InternshipLocationContextMixin,
                                       UpdateView):
    permission_required = ('internship.change_internship',)
    model = InternshipLocation
    form_class = InternshipLocationDeleteForm
    template_name = 'editor/helpers/modal/generic.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        message = '<strong>WARNING</strong>: '
        if self.object.validated:
            message += 'invalidating this location makes it unavailable for students to add additional journal entries.'
        else:
            message += 'students are not allowed to add journal entries until this location has been validated.'
        context['modal'] = get_modal(message, message_alert_css='m-0', message_type='warning',
                                     operation=('invalidated' if self.object.validated else 'validated'),
                                     target='#content-container',
                                     submit_icon=('building-dash' if self.object.validated else 'building-add'),
                                     submit_text=('Invalidate' if self.object.validated else 'Validate'),
                                     url=reverse('internship:journal:location:validate',
                                                 args=(self.kwargs['internship_id'], self.object.id,)))
        context['verbose_name'] = 'location'
        return {**context, **environs}

    def form_valid(self, form):
        form.instance.validated = not bool(self.object.validated)
        return super().form_valid(form)


class InternshipJournalEntryVerifyAllView(PermissionRequiredMixin, FormInvalidMixin, InternshipLocationContextMixin,
                                          UpdateView):
    permission_required = ('internship.change_internship',)
    model = InternshipLocation
    form_class = InternshipLocationDeleteForm
    template_name = 'editor/helpers/modal/generic.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        message = '<strong>WARNING</strong>: '
        message += ('verifying journal entries for this location prevents the student from making changes to them. '
                    'Verified journal entries are counted toward the student\'s total hours.')
        context['modal'] = get_modal(message, message_alert_css='m-0', message_type='warning',
                                     operation='verified', target='#content-container', submit_icon='journal-plus',
                                     submit_text='Verify All',
                                     url=reverse('internship:journal:location:verify',
                                                 args=(self.kwargs['internship_id'], self.object.id,)))
        context['verbose_name'] = 'journal entries'
        update_grade(self.request, self.kwargs['internship_id'])
        return {**context, **environs}

    def form_valid(self, form):
        self.object = form.save()
        entries = InternshipJournalEntry.objects.filter(location__internship_id=self.kwargs['internship_id'],
                                                        location_id=self.object.id,)
        for entry in entries:
            entry.verified = True
            entry.save()
        update_completed_hours(self.request, self.kwargs['internship_id'])
        update_grade(self.request, self.kwargs['internship_id'])
        return super().form_valid(form)

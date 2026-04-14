from core.views.funcs import get_cbv_context, get_environs, get_modal
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin, ListViewContextMixin, \
    SearchViewContextMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from editor.forms.registration.term import *


class TermArchiveView(PermissionRequiredMixin, FormInvalidMixin, UpdateView):
    permission_required = 'editor.change_term'
    model = Term
    form_class = TermArchiveDeleteForm
    template_name = 'core/modal/confirmation.html'
    success_url = reverse_lazy('editor:registration:term:list')

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        message = '<strong>WARNING</strong>: '
        if self.object.archived:
            message += 'de-archiving a term makes all content (including sections, master syllabi, segments, ' \
                       'and blocks) editable again. This operation should be used sparingly.'
        else:
            message += 'archiving a term makes all content (including sections, master syllabi, segments, and ' \
                       'blocks) no longer editable (for all users). Content can still be copied to future terms.'
        context['callback'] = 'done_reload_syllabi'
        context['modal'] = get_modal(message=message, message_alert_css='', message_type='warning',
                                     operation=('de-archived' if self.object.archived else 'archived'),
                                     target='#content-container',
                                     submit_icon='archive',
                                     submit_text=('De-archive' if self.object.archived else 'Archive'),
                                     url=reverse('editor:registration:term:archive', args=(self.object.id,)))
        return {**context, **environs}

    def form_valid(self, form):
        form.instance.archived = not bool(self.object.archived)
        master_syllabi = MasterSyllabus.objects.filter(term_id=self.object.id)
        for master_syllabus in master_syllabi:
            master_syllabus.locked = 1
            master_syllabus.save()
        return super().form_valid(form)


class TermCreateView(PermissionRequiredMixin, FormInvalidMixin, CreateView):
    permission_required = 'editor.add_term'
    model = Term
    form_class = TermForm
    template_name = 'core/offcanvas/add.html'
    success_url = reverse_lazy('editor:registration:term:list')

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:registration:term:create')
        context['target'] = '#content-container'
        return {**context, **environs}


class TermDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin, DeleteView):
    permission_required = 'editor.delete_term'
    model = Term
    form_class = TermArchiveDeleteForm
    success_url = reverse_lazy('editor:registration:term:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['url'] = reverse('editor:registration:term:delete', args=(self.object.id,))
        return context


class TermDetailView(PermissionRequiredMixin, ListViewContextMixin, ListView):
    permission_required = 'editor.view_term'
    model = Term

    def get_template_names(self):
        return ['editor/registration/card/card.html']


class TermListView(PermissionRequiredMixin, ListViewContextMixin, ListView):
    permission_required = 'editor.view_term'
    model = Term

    def get_template_names(self):
        return ['editor/registration/card/card.html']


class TermSearchView(PermissionRequiredMixin, SearchViewContextMixin, ListView):
    permission_required = 'editor.view_term'
    model = Term

    def get_template_names(self):
        return ['editor/registration/card/card.html']


class TermUpdateView(PermissionRequiredMixin, FormInvalidMixin, UpdateView):
    model = Term
    form_class = TermForm
    template_name = 'core/offcanvas/edit.html'
    success_url = reverse_lazy('editor:registration:term:list')

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['archive_perm'] = context['change_perm']
        if self.object.archived:
            context['change_perm'] = False
            context['delete_perm'] = False
        context['delete_url'] = None
        context['edit_url'] = reverse('editor:registration:term:update', args=(self.object.id,))
        context['target'] = '#content-container'
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(TermUpdateView, self).get_form_kwargs()
        kwargs.update({'archived': self.object.archived})
        return kwargs

    def has_permission(self):
        if self.request.user.has_perm('editor.change_term') or self.request.user.has_perm('editor.delete_term'):
            return True
        return False

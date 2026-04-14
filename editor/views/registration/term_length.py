from ...models import *
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin, ListViewContextMixin, \
    SearchViewContextMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from editor.forms.registration.term_length import *


class TermLengthCreateView(PermissionRequiredMixin, FormInvalidMixin, CreateView):
    permission_required = 'editor.add_term_length'
    model = TermLength
    form_class = TermLengthForm
    template_name = 'core/offcanvas/add.html'
    success_url = reverse_lazy('editor:registration:termlength:list')

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:registration:termlength:create')
        context['target'] = '#content-container'
        return {**context, **environs}


class TermLengthDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin, DeleteView):
    permission_required = 'editor.delete_term_length'
    model = TermLength
    form_class = TermLengthDeleteForm
    success_url = reverse_lazy('editor:registration:termlength:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['url'] = reverse('editor:registration:termlength:delete', args=(self.object.id,))
        return context


class TermLengthDetailView(PermissionRequiredMixin, ListViewContextMixin, ListView):
    permission_required = 'editor.view_termlength'
    model = TermLength

    def get_template_names(self):
        return ['editor/registration/card/card.html']


class TermLengthListView(PermissionRequiredMixin, ListViewContextMixin, ListView):
    permission_required = 'editor.view_term_length'
    model = TermLength

    def get_template_names(self):
        return ['editor/registration/card/card.html']


class TermLengthSearchView(PermissionRequiredMixin, SearchViewContextMixin, ListView):
    permission_required = 'editor.view_term_length'
    model = TermLength

    def get_template_names(self):
        return ['editor/registration/card/card.html']


class TermLengthUpdateView(PermissionRequiredMixin, FormInvalidMixin, UpdateView):
    model = TermLength
    form_class = TermLengthForm
    template_name = 'core/offcanvas/edit.html'
    success_url = reverse_lazy('editor:registration:termlength:list')

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = None
        context['edit_url'] = reverse('editor:registration:termlength:update', args=(self.object.id,))
        context['target'] = '#content-container'
        return {**context, **environs}

    def has_permission(self):
        if self.request.user.has_perm('editor.change_term_length') \
                or self.request.user.has_perm('editor.delete_term_length'):
            return True
        return False

from ..forms import QuickLinkForm, QuickLinkDeleteForm
from ..models import QuickLink
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView


class QuickLinkCreateView(PermissionRequiredMixin, FormInvalidMixin, CreateView):
    permission_required = ('editor.add_quicklink',)
    model = QuickLink
    form_class = QuickLinkForm
    success_url = reverse_lazy('editor:quicklink:list')
    template_name = 'core/offcanvas/add.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:quicklink:create')
        context['target'] = '#quick-links'
        return {**context, **environs}


class QuickLinkDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin,
                         DeleteView):
    permission_required = ('editor.delete_quicklink',)
    model = QuickLink
    form_class = QuickLinkDeleteForm
    success_url = reverse_lazy('editor:quicklink:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['target'] = '#quick-links'
        context['modal']['url'] = reverse('editor:quicklink:delete', args=(self.object.id,))
        return context


class QuickLinkListView(PermissionRequiredMixin, ListView):
    permission_required = ('editor.view_quicklink',)
    model = QuickLink
    template_name = 'editor/quicklinks/list.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        return {**context, **environs}


class QuickLinkUpdateView(PermissionRequiredMixin, FormInvalidMixin, UpdateView):
    permission_required = ('editor.change_quicklink', 'editor.delete_quicklink',)
    model = QuickLink
    form_class = QuickLinkForm
    success_url = reverse_lazy('editor:quicklink:list')
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = reverse('editor:quicklink:delete', args=(self.object.id,))
        context['edit_url'] = reverse('editor:quicklink:update', args=(self.object.id,))
        context['target'] = '#quick-links'
        return {**context, **environs}

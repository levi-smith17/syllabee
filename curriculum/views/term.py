from ..forms import TermForm, TermDeleteForm
from ..models import ProgramTerm
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView, View
from django.views.generic.base import ContextMixin


class TermContextMixin(ContextMixin, View):
    def get_success_url(self):
        return reverse('curriculum:program:detail', args=(self.kwargs['program_id'],))


class TermCreateView(PermissionRequiredMixin, TermContextMixin, FormInvalidMixin, CreateView):
    permission_required = ('curriculum.add_programterm',)
    model = ProgramTerm
    form_class = TermForm
    template_name = 'core/offcanvas/add.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('curriculum:program:term:create', args=(self.kwargs['program_id'],))
        context['target'] = '#content-container'
        return {**context, **environs}

    def form_valid(self, form):
        form.instance.program_id = self.kwargs['program_id']
        return super().form_valid(form)


class TermDeleteView(PermissionRequiredMixin, TermContextMixin, FormInvalidMixin, DeleteViewFormMixin, DeleteView):
    permission_required = ('curriculum.delete_programterm',)
    model = ProgramTerm
    form_class = TermDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['target'] = '#content-container'
        context['modal']['url'] = reverse('curriculum:program:term:delete',
                                          args=(self.kwargs['program_id'], self.object.id,))
        return context


class TermUpdateView(PermissionRequiredMixin, TermContextMixin, FormInvalidMixin, UpdateView):
    permission_required = ('curriculum.change_programterm', 'curriculum.delete_programterm',)
    model = ProgramTerm
    form_class = TermForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = None
        context['edit_url'] = reverse('curriculum:program:term:update',
                                      args=(self.kwargs['program_id'], self.object.id,))
        context['target'] = '#content-container'
        return {**context, **environs}

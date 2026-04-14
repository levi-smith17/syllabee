from ...forms import CourseRatioForm, CourseRatioDeleteForm
from ...models import CourseRatio
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin, ListViewContextMixin, \
    SearchViewContextMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from editor.forms.registration.course import *


class CourseRatioCreateView(PermissionRequiredMixin, FormInvalidMixin, CreateView):
    permission_required = 'editor.add_courseratio'
    model = CourseRatio
    form_class = CourseRatioForm
    template_name = 'core/offcanvas/add.html'
    success_url = reverse_lazy('editor:registration:courseratio:list')

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:registration:courseratio:create')
        context['target'] = '#content-container'
        return {**context, **environs}


class CourseRatioDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin, DeleteView):
    permission_required = 'editor.delete_courseratio'
    model = CourseRatio
    form_class = CourseRatioDeleteForm
    success_url = reverse_lazy('editor:registration:courseratio:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['url'] = reverse('editor:registration:courseratio:delete', args=(self.object.id,))
        return context


class CourseRatioDetailView(PermissionRequiredMixin, ListViewContextMixin, ListView):
    permission_required = 'editor.view_courseratio'
    model = CourseRatio

    def get_template_names(self):
        return ['editor/registration/card/card.html']


class CourseRatioListView(PermissionRequiredMixin, ListViewContextMixin, ListView):
    permission_required = 'editor.view_courseratio'
    model = CourseRatio

    def get_template_names(self):
        return ['editor/registration/card/card.html']


class CourseRatioSearchView(PermissionRequiredMixin, SearchViewContextMixin, ListView):
    permission_required = 'editor.view_courseratio'
    model = CourseRatio

    def get_template_names(self):
        return ['editor/registration/card/card.html']


class CourseRatioUpdateView(PermissionRequiredMixin, FormInvalidMixin, UpdateView):
    permission_required = ('editor.change_courseratio', 'editor.delete_courseratio',)
    model = CourseRatio
    form_class = CourseRatioForm
    template_name = 'core/offcanvas/edit.html'
    success_url = reverse_lazy('editor:registration:courseratio:list')

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = None
        context['edit_url'] = reverse('editor:registration:courseratio:update', args=(self.object.id,))
        context['target'] = '#content-container'
        return {**context, **environs}

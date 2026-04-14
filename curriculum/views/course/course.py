from ...forms import CourseCreateForm, CourseDeleteForm, CourseUpdateForm
from ...models import ProgramCourse
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView, View
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin


class CourseContextMixin(ContextMixin, View):
    def get_success_url(self):
        return reverse('curriculum:program:detail', args=(self.kwargs['program_id'],))


class CourseFormMixin(FormMixin, View):
    def get_form_kwargs(self):
        kwargs = super(CourseFormMixin, self).get_form_kwargs()
        kwargs.update({'program_id': self.kwargs['program_id']})
        return kwargs


class CourseCreateView(PermissionRequiredMixin, CourseContextMixin, CourseFormMixin, FormInvalidMixin, CreateView):
    permission_required = ('curriculum.add_programcourse',)
    model = ProgramCourse
    form_class = CourseCreateForm
    template_name = 'core/offcanvas/add.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('curriculum:program:term:course:create',
                                     args=(self.kwargs['program_id'], self.kwargs['term_id'],))
        context['target'] = '#content-container'
        return {**context, **environs}

    def form_valid(self, form):
        form.instance.term_id = self.kwargs['term_id']
        return super().form_valid(form)


class CourseDeleteView(PermissionRequiredMixin, CourseContextMixin, FormInvalidMixin, DeleteViewFormMixin, DeleteView):
    permission_required = ('curriculum.delete_programcourse',)
    model = ProgramCourse
    form_class = CourseDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['target'] = '#content-container'
        context['modal']['url'] = reverse('curriculum:program:term:course:delete',
                                          args=(self.kwargs['program_id'], self.kwargs['term_id'], self.object.id,))
        return context


class CourseUpdateView(PermissionRequiredMixin, CourseContextMixin, CourseFormMixin, FormInvalidMixin, UpdateView):
    permission_required = ('curriculum.change_programcourse', 'curriculum.delete_programcourse',)
    model = ProgramCourse
    form_class = CourseUpdateForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = None
        context['edit_url'] = reverse('curriculum:program:term:course:update',
                                      args=(self.kwargs['program_id'], self.kwargs['term_id'], self.object.id,))
        context['target'] = '#content-container'
        return {**context, **environs}

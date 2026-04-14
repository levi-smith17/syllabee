from ...forms import CourseExtensionForm, CourseExtensionDeleteForm
from ...models import Program, ProgramCourse, ProgramCourseExtension, ProgramTerm
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView, TemplateView, View
from django.views.generic.base import ContextMixin


class CourseExtensionContextMixin(ContextMixin, View):
    def get_success_url(self):
        return reverse('curriculum:program:term:course:extension:detail',
                       args=(self.kwargs['program_id'], self.kwargs['term_id'], self.kwargs['course_id']))


class CourseExtensionCreateView(PermissionRequiredMixin, CourseExtensionContextMixin, FormInvalidMixin, CreateView):
    permission_required = ('curriculum.add_programcourseextension',)
    model = ProgramCourseExtension
    form_class = CourseExtensionForm
    template_name = 'core/offcanvas/add.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('curriculum:program:term:course:extension:create',
                                     args=(self.kwargs['program_id'], self.kwargs['term_id'],
                                           self.kwargs['course_id'],))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}

    def form_valid(self, form):
        course = ProgramCourse.objects.get(pk=self.kwargs['course_id'])
        form.instance.related_course_id = course.course.id
        form.instance.term_id = self.kwargs['term_id']
        return super().form_valid(form)


class CourseExtensionDeleteView(PermissionRequiredMixin, CourseExtensionContextMixin, FormInvalidMixin,
                                DeleteViewFormMixin, DeleteView):
    permission_required = ('curriculum.delete_programcourseextension',)
    model = ProgramCourseExtension
    form_class = CourseExtensionDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['target'] = '.offcanvas-full-container'
        context['modal']['url'] = reverse('curriculum:program:term:course:extension:delete',
                                          args=(self.kwargs['program_id'], self.kwargs['term_id'],
                                                self.kwargs['course_id'], self.object.id,))
        return context


class CourseExtensionDetailView(PermissionRequiredMixin, TemplateView):
    permission_required = ('curriculum.change_programcourse',)
    template_name = 'curriculum/program/term/course/extensions.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['course'] = ProgramCourse.objects.get(pk=self.kwargs['course_id'])
        context['extensions'] = (ProgramCourseExtension.objects.filter(related_course=context['course'].course)
                                 .order_by('course__course_code'))
        context['program'] = Program.objects.get(pk=self.kwargs['program_id'])
        context['term'] = ProgramTerm.objects.get(pk=self.kwargs['term_id'])
        return {**context, **environs}


class CourseExtensionUpdateView(PermissionRequiredMixin, CourseExtensionContextMixin, FormInvalidMixin, UpdateView):
    permission_required = ('curriculum.change_programcourseextension', 'curriculum.delete_programcourseextension',)
    model = ProgramCourseExtension
    form_class = CourseExtensionForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = None
        context['edit_url'] = reverse('curriculum:program:term:course:extension:update',
                                      args=(self.kwargs['program_id'], self.kwargs['term_id'], self.kwargs['course_id'],
                                            self.object.id,))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}

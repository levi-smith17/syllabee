from ...forms import CourseRequisiteBlockForm, CourseRequisiteBlockDeleteForm
from ...models import Course, CourseRequisite, CourseRequisiteBlock
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin,FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView, View
from django.views.generic.base import ContextMixin


class CourseRequisiteContextMixin(ContextMixin, View):
    def get_success_url(self):
        return reverse('editor:registration:course:block:detail', args=(self.kwargs['course_id'],))


class CourseRequisiteBlockCreateView(PermissionRequiredMixin, CourseRequisiteContextMixin, FormInvalidMixin,
                                     CreateView):
    permission_required = ('editor.add_course',)
    model = CourseRequisiteBlock
    form_class = CourseRequisiteBlockForm
    template_name = 'core/offcanvas/add.html'

    def form_valid(self, form):
        max_order = CourseRequisiteBlock.objects.filter(course_id=self.kwargs['course_id']).order_by('-order').first()
        form.instance.order = ((max_order.order + 10) if max_order else 10)
        form.instance.course_id = self.kwargs['course_id']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:registration:course:block:create',
                                     args=(self.kwargs['course_id'],))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}


class CourseRequisiteBlockDeleteView(PermissionRequiredMixin, CourseRequisiteContextMixin, FormInvalidMixin,
                                     DeleteViewFormMixin, DeleteView):
    permission_required = ('editor.delete_course',)
    model = CourseRequisiteBlock
    form_class = CourseRequisiteBlockDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['url'] = reverse('editor:registration:course:block:delete',
                                          args=(self.kwargs['course_id'], self.object.id,))
        context['modal']['target'] = '.offcanvas-full-container'
        return context


class CourseRequisiteBlockDetailView(PermissionRequiredMixin, TemplateView):
    permission_required = ('editor.change_course',)
    template_name = 'editor/registration/course/requisites.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['course'] = Course.objects.get(pk=self.kwargs['course_id'])
        context['requisite_blocks'] = (CourseRequisiteBlock.objects.filter(course_id=self.kwargs['course_id'])
                                       .order_by('order'))
        return {**context, **environs}


class CourseRequisiteBlockUpdateView(PermissionRequiredMixin, CourseRequisiteContextMixin, FormInvalidMixin,
                                     UpdateView):
    permission_required = ('editor.change_courserequisiteblock', 'editor.delete_courserequisiteblock',)
    model = CourseRequisiteBlock
    form_class = CourseRequisiteBlockForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = reverse('editor:registration:course:block:delete',
                                        args=(self.kwargs['course_id'], self.object.id,))
        context['edit_url'] = reverse('editor:registration:course:block:update',
                                      args=(self.kwargs['course_id'], self.object.id,))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}

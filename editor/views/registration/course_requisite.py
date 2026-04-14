from ...forms import CourseRequisiteForm, CourseRequisiteDeleteForm
from ...models import CourseRequisite
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin,FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView
from editor.views.registration.course_requisite_block import CourseRequisiteContextMixin


class CourseRequisiteCreateView(PermissionRequiredMixin, CourseRequisiteContextMixin, FormInvalidMixin, CreateView):
    permission_required = ('editor.add_course',)
    model = CourseRequisite
    form_class = CourseRequisiteForm
    template_name = 'core/offcanvas/add.html'

    def form_valid(self, form):
        max_order = CourseRequisite.objects.filter(requisite_block_id=self.kwargs['block_id']).order_by('-order').first()
        form.instance.order = ((max_order.order + 10) if max_order else 10)
        form.instance.requisite_block_id = self.kwargs['block_id']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:registration:course:block:requisite:create',
                                     args=(self.kwargs['course_id'], self.kwargs['block_id'],))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}


class CourseRequisiteDeleteView(PermissionRequiredMixin, CourseRequisiteContextMixin, FormInvalidMixin,
                                DeleteViewFormMixin, DeleteView):
    permission_required = ('editor.delete_course',)
    model = CourseRequisite
    form_class = CourseRequisiteDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['url'] = reverse('editor:registration:course:block:requisite:delete',
                                          args=(self.kwargs['course_id'], self.kwargs['block_id'], self.object.id,))
        context['modal']['target'] = '.offcanvas-full-container'
        return context


class CourseRequisiteUpdateView(PermissionRequiredMixin, CourseRequisiteContextMixin, FormInvalidMixin, UpdateView):
    permission_required = ('editor.change_courserequisite', 'editor.delete_courserequisite',)
    model = CourseRequisite
    form_class = CourseRequisiteForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = reverse('editor:registration:course:block:requisite:delete',
                                        args=(self.kwargs['course_id'], self.kwargs['block_id'], self.object.id,))
        context['edit_url'] = reverse('editor:registration:course:block:requisite:update',
                                      args=(self.kwargs['course_id'], self.kwargs['block_id'], self.object.id,))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}

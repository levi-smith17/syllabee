from editor.forms import *
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView, View
from django.views.generic.edit import FormMixin


class ScheduleUnitFormMixin(FormMixin, View):
    def get_form_kwargs(self):
        kwargs = super(ScheduleUnitFormMixin, self).get_form_kwargs()
        kwargs.update({'schedule_id': self.kwargs['schedule_id']})
        return kwargs

    def get_success_url(self):
        return reverse('editor:block:schedule:update', args=(self.kwargs['master_syllabus_id'],
                                                            self.kwargs['segment_id'], self.kwargs['block_id'],))


class ScheduleUnitCreateView(PermissionRequiredMixin, FormInvalidMixin, ScheduleUnitFormMixin, CreateView):
    permission_required = 'editor.add_scheduleunit'
    model = ScheduleUnit
    form_class = ScheduleUnitForm
    template_name = 'core/offcanvas/add.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:block:schedule:unit:create',
                                     args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                           self.kwargs['block_id'], self.kwargs['schedule_id'],))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}

    def form_valid(self, form):
        form.instance.schedule = Schedule.objects.get(pk=self.kwargs['schedule_id'])
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ScheduleUnitDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin, DeleteView):
    permission_required = 'editor.delete_scheduleunit'
    model = ScheduleUnit
    form_class = ScheduleUnitDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['target'] = '.offcanvas-full-container'
        context['modal']['url'] = reverse('editor:block:schedule:unit:delete',
                                          args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                self.kwargs['block_id'], self.kwargs['schedule_id'], self.object.id,))
        return context

    def get_success_url(self):
        return reverse('editor:block:schedule:update', args=(self.kwargs['master_syllabus_id'],
                                                            self.kwargs['segment_id'], self.kwargs['block_id'],))


class ScheduleUnitUpdateView(PermissionRequiredMixin, FormInvalidMixin, ScheduleUnitFormMixin, UpdateView):
    model = ScheduleUnit
    form_class = ScheduleUnitForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = reverse('editor:block:schedule:unit:delete',
                                        args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                              self.kwargs['block_id'], self.kwargs['schedule_id'], self.object.id,))
        context['edit_url'] = reverse('editor:block:schedule:unit:update',
                                      args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                            self.kwargs['block_id'], self.kwargs['schedule_id'], self.object.id,))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}

    def has_permission(self):
        if self.request.user.has_perm('editor.change_scheduleunit') or \
                self.request.user.has_perm('editor.delete_scheduleunit'):
            return True
        return False

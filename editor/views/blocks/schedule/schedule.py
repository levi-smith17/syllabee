from editor.forms import *
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import UpdateView, View
from django.views.generic.base import ContextMixin
from editor.views.blocks.schedule.funcs import render_schedule


class ScheduleContextMixin(ContextMixin, View):
    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super(ScheduleContextMixin, self).get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['schedule_table'] = render_schedule(self.request, self.object, self.object.effective_term, 'edit')
        return {**context, **environs}


class SchedulePropertiesUpdateView(PermissionRequiredMixin, FormInvalidMixin, UpdateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'core/offcanvas/edit.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = False
        context['edit_url'] = reverse('editor:block:schedule:update_properties', args=(self.kwargs['master_syllabus_id'],
                                                                                      self.kwargs['segment_id'],
                                                                                      self.kwargs['block_id'],
                                                                                      self.object.id,))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(SchedulePropertiesUpdateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse('editor:block:schedule:update', args=(self.kwargs['master_syllabus_id'],
                                                            self.kwargs['segment_id'], self.kwargs['block_id'],))

    def has_permission(self):
        if self.request.user.has_perm('editor.change_schedule') or self.request.user.has_perm('editor.delete_schedule'):
            return True
        return False

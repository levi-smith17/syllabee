from editor.forms import *
from core.views.funcs import get_cbv_context, get_environs, get_modal
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import AccessMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, FormView, UpdateView, View
from django.views.generic.edit import FormMixin


class ScheduleTopicAccessMixin(AccessMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if 'pk' not in self.kwargs:  # We're attempting to add a schedule topic.
            schedule = Schedule.objects.get(pk=self.kwargs['schedule_id'])
            unit_count = ScheduleUnit.objects.filter(schedule=schedule).count()
            if unit_count == 0:
                return self.handle_no_permission()
        return super(ScheduleTopicAccessMixin, self).dispatch(request, *args, **kwargs)

    def get_permission_denied_message(self):
        self.permission_denied_message = 'At least one unit must be created before you can create a topic.'
        return self.permission_denied_message


class ScheduleTopicFormMixin(FormMixin, View):
    def get_form_class(self):
        modelform = super().get_form_class()
        modelform.base_fields['unit'].limit_choices_to = {'schedule__id': self.kwargs['schedule_id']}
        return modelform

    def get_form_kwargs(self):
        kwargs = super(ScheduleTopicFormMixin, self).get_form_kwargs()
        kwargs.update({'schedule_id': self.kwargs['schedule_id']})
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse('editor:block:schedule:update', args=(self.kwargs['master_syllabus_id'],
                                                            self.kwargs['segment_id'], self.kwargs['block_id'],))


class ScheduleTopicCreateView(PermissionRequiredMixin, ScheduleTopicAccessMixin, FormInvalidMixin,
                              ScheduleTopicFormMixin, CreateView):
    permission_required = 'editor.add_scheduletopic'
    model = ScheduleTopic
    form_class = ScheduleTopicForm
    template_name = 'core/offcanvas/add.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:block:schedule:topic:create',
                                     args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                           self.kwargs['block_id'], self.kwargs['schedule_id'],))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}


class ScheduleTopicCopyView(PermissionRequiredMixin, FormInvalidMixin, FormView):
    permission_required = 'editor.add_scheduletopic'
    form_class = ScheduleTopicDeleteForm
    model = ScheduleTopic
    template_name = 'editor/helpers/modal/generic.html'

    def form_valid(self, form):
        topic = ScheduleTopic.objects.get(pk=self.kwargs['pk'])
        topic.pk = None
        topic.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['modal'] = get_modal(message='<strong>WARNING</strong>: are you sure that you want to copy this topic? '
                                             'The new topic will be linked to the same unit and contain the same '
                                             'information.',
                                     message_alert_css='m-0', message_type='warning', operation='copied',
                                     target='.offcanvas-full-container', submit_icon='clipboard', submit_text='Copy',
                                     url=reverse('editor:block:schedule:topic:copy',
                                                 args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                       self.kwargs['block_id'], self.kwargs['schedule_id'],
                                                       self.kwargs['pk'],)))
        return {**context, **environs}

    def get_success_url(self):
        return reverse('editor:block:schedule:update', args=(self.kwargs['master_syllabus_id'],
                                                            self.kwargs['segment_id'], self.kwargs['block_id'],))


class ScheduleTopicDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin, DeleteView):
    permission_required = 'editor.delete_scheduletopic'
    model = ScheduleTopic
    form_class = ScheduleTopicDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['target'] = '.offcanvas-full-container'
        context['modal']['url'] = reverse('editor:block:schedule:topic:delete',
                                          args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                self.kwargs['block_id'], self.kwargs['schedule_id'], self.object.id,))
        return context

    def get_success_url(self):
        return reverse('editor:block:schedule:update', args=(self.kwargs['master_syllabus_id'],
                                                            self.kwargs['segment_id'], self.kwargs['block_id'],))


class ScheduleTopicUpdateView(PermissionRequiredMixin, FormInvalidMixin, ScheduleTopicFormMixin, UpdateView):
    model = ScheduleTopic
    form_class = ScheduleTopicForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = reverse('editor:block:schedule:topic:delete',
                                        args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                              self.kwargs['block_id'], self.kwargs['schedule_id'], self.object.id,))
        context['edit_url'] = reverse('editor:block:schedule:topic:update',
                                      args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                            self.kwargs['block_id'], self.kwargs['schedule_id'], self.object.id,))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}

    def has_permission(self):
        if self.request.user.has_perm('editor.change_scheduletopic') or \
                self.request.user.has_perm('editor.delete_scheduletopic'):
            return True
        return False

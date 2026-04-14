from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView, View
from django.views.generic.edit import FormMixin
from editor.forms.blocks.schedule import *


class OverrideFormMixin(FormMixin, View):
    def get_form_kwargs(self):
        kwargs = super(OverrideFormMixin, self).get_form_kwargs()
        kwargs.update({'master_syllabus_id': self.kwargs['master_syllabus_id']})
        kwargs.update({'segment_id': self.kwargs['segment_id']})
        kwargs.update({'schedule_id': self.kwargs['schedule_id']})
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse('editor:block:detail', args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                   self.kwargs['block_id'],))


class OverrideCreateView(PermissionRequiredMixin, FormInvalidMixin, OverrideFormMixin, CreateView):
    permission_required = 'editor.add_override'
    model = Override
    form_class = OverrideCreateForm
    template_name = 'core/offcanvas/add.html'

    def form_valid(self, form):
        master_section = (MasterBondSection.objects
                          .filter(master_bond__master_syllabus_id=self.kwargs['master_syllabus_id'],
                                  master_bond__segment_id=self.kwargs['segment_id'],
                                  section__isnull=False, owner=self.request.user).first())
        form.instance.section = master_section.section
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:block:schedule:override:create', args=(self.kwargs['master_syllabus_id'],
                                                                                   self.kwargs['segment_id'],
                                                                                   self.kwargs['block_id'],
                                                                                   self.kwargs['schedule_id'],))
        context['target'] = '#segment-' + str(self.kwargs['segment_id']) + '-block-' + str(self.kwargs['block_id']) + \
                            '-content'
        return {**context, **environs}


class OverrideDeleteView(PermissionRequiredMixin, FormInvalidMixin, OverrideFormMixin, DeleteViewFormMixin,
                         DeleteView):
    permission_required = 'editor.delete_override'
    model = Override
    form_class = OverrideDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['target'] = '#segment-' + str(self.kwargs['segment_id']) + '-block-' + \
                                     str(self.kwargs['block_id']) + '-content'
        context['modal']['url'] = reverse('editor:block:schedule:override:delete',
                                          args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                self.kwargs['block_id'], self.kwargs['schedule_id'], self.object.id,))
        return context


class OverrideUpdateView(PermissionRequiredMixin, FormInvalidMixin, OverrideFormMixin, UpdateView):
    model = Override
    form_class = OverrideForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = reverse('editor:block:schedule:override:delete', args=(self.kwargs['master_syllabus_id'],
                                                                                      self.kwargs['segment_id'],
                                                                                      self.kwargs['block_id'],
                                                                                      self.kwargs['schedule_id'],
                                                                                      self.object.id,))
        context['edit_url'] = reverse('editor:block:schedule:override:update', args=(self.kwargs['master_syllabus_id'],
                                                                                    self.kwargs['segment_id'],
                                                                                    self.kwargs['block_id'],
                                                                                    self.kwargs['schedule_id'],
                                                                                    self.object.id,))
        context['target'] = '#segment-' + str(self.kwargs['segment_id']) + '-block-' + str(self.kwargs['block_id']) + \
                            '-content'
        return {**context, **environs}

    def has_permission(self):
        if self.request.user.has_perm('editor.change_override') or self.request.user.has_perm('editor.delete_override'):
            return True
        return False

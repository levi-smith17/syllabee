from ..forms import *
from .mixins import MasterSyllabusLockedAccessMixin, MasterSyllabusTocContextMixin
from core.forms.core import ArrangeForm
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import DeleteView, FormView, ListView, TemplateView, UpdateView


class MasterBondArrangeView(PermissionRequiredMixin, MasterSyllabusLockedAccessMixin, FormInvalidMixin,
                            MasterSyllabusTocContextMixin, FormView):
    permission_required = ('editor.change_masterbond',)
    form_class = ArrangeForm
    template_name = 'editor/helpers/offcanvas/arrange.html'

    def form_valid(self, form):
        order = 10
        ordering = form.cleaned_data['ordering'].split('|')
        for segment_id in ordering:
            master_bond = MasterBond.objects.get(master_syllabus_id=self.kwargs['master_syllabus_id'],
                                                 segment_id=segment_id)
            master_bond.order = order
            master_bond.save()
            order += 10
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['callback'] = 'done_generic'
        context['modal'] = {}
        context['modal']['items'] = (Segment.objects
                                     .filter(masterbond__master_syllabus_id=self.kwargs['master_syllabus_id'])
                                     .order_by('masterbond__order'))
        context['modal']['message'] = '<strong>NOTE</strong>: to rearrange the segments on this master syllabus, ' \
                                      'first select a segment from the list below, then use the up and down arrow ' \
                                      'buttons to reorder the segments, and then click the Save button to save your ' \
                                      'changes.'
        context['modal']['message_type'] = 'info'
        context['modal']['model'] = 'master syllabus'
        context['modal']['target'] = '#toc-container'
        context['modal']['url'] = reverse('editor:masterbond:arrange', args=(self.kwargs['master_syllabus_id'],))
        return {**context, **environs}


class MasterBondCreateView(PermissionRequiredMixin, MasterSyllabusLockedAccessMixin, MasterSyllabusTocContextMixin,
                           TemplateView):
    permission_required = ('editor.add_masterbond',)
    template_name = 'editor/mastersyllabus/masterbond/library.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['add_url'] = reverse('editor:masterbond:create', args=(self.kwargs['master_syllabus_id'],))
        context['callback'] = 'done_close_full'
        context['master_syllabus_id'] = self.kwargs['master_syllabus_id']
        context['target'] = '#toc-container'
        context['segments'] = (Segment.objects
                               .filter(owner=self.request.user)
                               .exclude(masterbond__master_syllabus_id=self.kwargs['master_syllabus_id'])
                               .order_by('name')
                               .distinct())
        return {**context, **environs}


class MasterBondDeleteView(PermissionRequiredMixin, FormInvalidMixin, MasterSyllabusLockedAccessMixin,
                           MasterSyllabusTocContextMixin, DeleteViewFormMixin, DeleteView):
    permission_required = ('editor.delete_masterbond',)
    model = MasterBond
    form_class = MasterBondDeleteForm

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['callback'] = 'done_load_content'
        context['content_id'] = 'segment-' + str(self.object.segment.id)
        context['modal'] = {}
        context['modal']['message'] = 'Are you sure you want to remove the following segment? Content can be ' \
                                      'relinked using the <strong>Copy Content</strong> option.'
        context['modal']['message_alert_css'] = None
        context['modal']['message_type'] = 'warning'
        context['modal']['operation'] = 'removed'
        context['modal']['target'] = '#toc-container'
        context['modal']['url'] = reverse('editor:masterbond:delete', args=(self.kwargs['master_syllabus_id'],
                                                                           self.object.id,))
        context['verbose_name'] = 'segment'
        return {**context, **environs}


class MasterBondListView(PermissionRequiredMixin, ListView):
    permission_required = ('editor.view_masterbond',)
    model = MasterBond
    template_name = 'editor/mastersyllabus/segment/list.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['master_bonds'] = MasterBond.objects.filter(master_syllabus_id=self.kwargs['master_syllabus_id'])
        context['master_syllabus'] = MasterSyllabus.objects.get(pk=self.kwargs['master_syllabus_id'])
        context['segment_id'] = 1
        return {**context, **environs}


class MasterBondSearchView(PermissionRequiredMixin, ListView):
    permission_required = ('editor.view_masterbond',)
    model = Segment

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['master_syllabus_id'] = self.kwargs['master_syllabus_id']
        context['segments'] = (Segment.objects
                               .filter(owner=self.request.user, name__icontains=self.request.GET.get('pattern', ''))
                               .exclude(Q(masterbond__master_syllabus_id=self.kwargs['master_syllabus_id']))
                               .order_by('name')
                               .distinct())
        return {**environs, **context}

    def get_template_names(self):
        return ['editor/mastersyllabus/masterbond/results.html']


class MasterBondVisibilityView(PermissionRequiredMixin, MasterSyllabusLockedAccessMixin, FormInvalidMixin,
                               MasterSyllabusTocContextMixin, UpdateView):
    permission_required = ('editor.change_masterbond',)
    model = MasterBond
    form_class = MasterBondVisibilityForm
    template_name = 'core/modal/confirmation.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        return {**context, **environs}

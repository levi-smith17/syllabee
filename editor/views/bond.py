from ..forms import *
from .funcs import is_segment_archived, is_segment_previously_published, replace_segment
from .mixins import MasterSyllabusLockedAccessMixin
from core.forms import ArrangeForm
from core.views.funcs import get_cbv_context, get_environs, get_modal
from core.views.mixins import FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DeleteView, DetailView, FormView, ListView, TemplateView, View
from django.views.generic.base import ContextMixin


class BondContextMixin(ContextMixin, View):
    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:bond:create', args=(self.kwargs['master_syllabus_id'],
                                                                self.kwargs['segment_id'],))
        context['blocks'] = (Block.objects
                             .filter(owner=self.request.user)
                             .exclude(Q(bond__segment_id=self.kwargs['segment_id']) |
                                      Q(printableblock__gradedeterminationblock__isnull=False) |
                                      Q(printableblock__fileblock__coursesyllabusblock__isnull=False))
                             .order_by('name')
                             .distinct())
        context['master_bond'] = MasterBond.objects.get(master_syllabus_id=self.kwargs['master_syllabus_id'],
                                                        segment_id=self.kwargs['segment_id'])
        context['master_syllabus'] = MasterSyllabus.objects.get(pk=self.kwargs['master_syllabus_id'])
        context['target'] = '#content-container'
        context['segment'] = Segment.objects.get(pk=self.kwargs['segment_id'])
        return {**context, **environs}


class BondArrangeView(PermissionRequiredMixin, MasterSyllabusLockedAccessMixin, FormInvalidMixin, FormView):
    permission_required = ('editor.change_bond',)
    form_class = ArrangeForm
    template_name = 'editor/helpers/offcanvas/arrange.html'

    def form_valid(self, form):
        order = 10
        ordering = form.cleaned_data['ordering'].split('|')
        for block_id in ordering:
            bond = Bond.objects.get(segment_id=self.kwargs['segment_id'], block_id=block_id)
            bond.order = order
            bond.save()
            order += 10
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['callback'] = 'done_generic'
        context['modal'] = {}
        context['modal']['items'] = (Block.objects
                                     .filter(bond__segment_id=self.kwargs['segment_id'])
                                     .order_by('bond__order'))
        context['modal']['message'] = '<strong>NOTE</strong>: to rearrange the blocks on this segment, first select ' \
                                      'a block from the list below, then use the up and down arrow buttons to ' \
                                      'reorder the blocks, and then click the Save button to save your changes.'
        context['modal']['message_type'] = 'info'
        context['modal']['model'] = 'segment'
        context['modal']['target'] = '#content-container'
        context['modal']['url'] = reverse('editor:bond:arrange', args=(self.kwargs['master_syllabus_id'],
                                                                      self.kwargs['segment_id'],))
        return {**context, **environs}

    def get_success_url(self):
        return reverse('editor:mastersyllabus:segment:detail', args=(self.kwargs['master_syllabus_id'],
                                                     self.kwargs['segment_id']))

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            if is_segment_archived(self.kwargs['segment_id']) or \
                    is_segment_previously_published(self.kwargs['segment_id'], self.kwargs['master_syllabus_id']):
                self.kwargs['segment_id'] = replace_segment(request, self.kwargs['master_syllabus_id'],
                                                            self.kwargs['segment_id'])
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class BondCreateView(PermissionRequiredMixin, MasterSyllabusLockedAccessMixin, TemplateView):
    permission_required = ('editor.add_bond',)
    template_name = 'editor/mastersyllabus/segment/bond/library.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['add_url'] = reverse('editor:bond:create', args=(self.kwargs['master_syllabus_id'],
                                                                self.kwargs['segment_id'],))
        context['callback'] = 'done_close_full'
        context['master_bond'] = MasterBond.objects.get(master_syllabus_id=self.kwargs['master_syllabus_id'],
                                                        segment_id=self.kwargs['segment_id'])
        context['master_syllabus_id'] = self.kwargs['master_syllabus_id']
        context['target'] = '#content-container'
        context['segment_id'] = self.kwargs['segment_id']
        return {**context, **environs}

    def get_success_url(self):
        return reverse('editor:mastersyllabus:segment:detail', args=(self.kwargs['master_syllabus_id'],
                                                     self.kwargs['segment_id']))


class BondDeleteView(PermissionRequiredMixin, MasterSyllabusLockedAccessMixin, FormInvalidMixin, DeleteView):
    permission_required = ('editor.delete_bond',)
    model = Bond
    form_class = BondDeleteForm
    template_name = 'core/modal/confirmation.html'

    def form_valid(self, form):
        if is_segment_archived(self.kwargs['segment_id']) or \
                is_segment_previously_published(self.kwargs['segment_id'], self.kwargs['master_syllabus_id']):
            self.kwargs['segment_id'] = replace_segment(self.request, self.kwargs['master_syllabus_id'],
                                                        self.kwargs['segment_id'])
            self.object = Bond.objects.get(segment_id=self.kwargs['segment_id'], block_id=self.object.block.id)
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['modal'] = {}
        context['modal']['message'] = 'Are you sure you want to remove the following block? Content can be relinked ' \
                                      'using the <strong>Copy Content</strong> option.'
        context['modal']['message_alert_css'] = None
        context['modal']['message_type'] = 'warning'
        context['modal']['operation'] = 'removed'
        context['modal']['target'] = '#content-container'
        context['modal']['url'] = reverse('editor:bond:delete', args=(self.kwargs['master_syllabus_id'],
                                                                     self.kwargs['segment_id'],
                                                                     self.object.id,))
        context['verbose_name'] = 'block'
        return {**context, **environs}

    def get_success_url(self):
        return reverse('editor:mastersyllabus:segment:detail', args=(self.kwargs['master_syllabus_id'],
                                                     self.kwargs['segment_id']))


class BondDetailView(PermissionRequiredMixin, DetailView):
    permission_required = ('editor.view_bond',)
    model = Block
    template_name = 'editor/mastersyllabus/segment/bond/block.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['block'] = Block.objects.get(pk=self.kwargs['pk'])
        context['master_syllabus'] = MasterSyllabus.objects.get(pk=self.kwargs['master_syllabus_id'])
        context['render_mode'] = 'view'
        context['term'] = context['master_syllabus'].term
        context['segment'] = Segment.objects.get(pk=self.kwargs['segment_id'])
        context['bond'] = {}
        context['bond']['block'] = context['block']
        context['bond']['segment'] = context['segment']
        return {**context, **environs}


class BondListView(PermissionRequiredMixin, ListView):
    permission_required = ('editor.view_bond',)
    model = Block
    template_name = 'editor/helpers/modal/generic.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        master_syllabi = (MasterSyllabus.objects
                          .filter(masterbond__segment__bond__block_id=self.kwargs['block_id'])
                          .distinct())
        html = '<div class="alert alert-info m-0" role="alert">'
        html += '<strong>' + str(Block.objects.get(pk=self.kwargs['block_id'])) + '</strong>'
        html += '</div>'
        if master_syllabi:
            html += '<div class="accordion mt-3" id="block-library-associations-accordion">'
            for master_syllabus in master_syllabi:
                html += '<div class="accordion-item">'
                html += '<div class="accordion-header" id="block-associations-' + str(master_syllabus.id) + '-header">'
                html += '<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" ' \
                        'data-bs-target="#block-associations-' + \
                        str(master_syllabus.id) + '" aria-expanded="false" aria-controls="block-associations-' + \
                        str(master_syllabus.id) + '">'
                html += str(master_syllabus)
                html += '</button>'
                html += '</div>'
                html += '<div id="block-associations-' + str(master_syllabus.id) + \
                        '" class="accordion-collapse collapse" aria-labelledby="block-associations-' + \
                        str(master_syllabus.id) + '" data-bs-parent="#block-library-associations-accordion">'
                html += '<div class="accordion-body p-0">'
                html += '<ul class="list-group list-group-flush">'
                segments = Segment.objects.filter(masterbond__master_syllabus=master_syllabus,
                                                  bond__block_id=self.kwargs['block_id'])
                for segment in segments:
                    html += '<li class="list-group-item ps-4 border-secondary text-bg-' + \
                            environs['profile']['theme'] + '">' + segment.name + '</li>'
                html += '</ul>'
                html += '</div>'
                html += '</div>'
                html += '</div>'
            html += '</div>'
        if master_syllabi:
            message = '<strong>NOTE</strong>: this block is currently linked to the master syllabi listed below. ' \
                      'Expand each master syllabus to view the specific segment that this block is linked to.'
            message_type = 'info'
        else:
            message = '<strong>WARNING</strong>: this block is not currently linked to any master syllabi.'
            message_type = 'warning'
        context['modal'] = get_modal(message=message, message_type=message_type)
        context['content'] = html
        context['verbose_name'] = 'block'
        return {**context, **environs}


class BondSearchView(PermissionRequiredMixin, BondContextMixin, ListView):
    permission_required = ('editor.view_bond',)
    model = Block

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['blocks'] = (Block.objects
                             .filter(owner=self.request.user, name__icontains=self.request.GET.get('pattern', ''))
                             .exclude(Q(bond__segment_id=self.kwargs['segment_id']) |
                                      Q(printableblock__gradedeterminationblock__isnull=False) |
                                      Q(printableblock__fileblock__coursesyllabusblock__isnull=False))
                             .order_by('name')
                             .distinct())
        return {**environs, **context}

    def get_template_names(self):
        return ['editor/mastersyllabus/segment/bond/results.html']

from ..forms import *
from .funcs import (is_addendum_necessary, is_block_archived, is_block_previously_published, is_master_syllabus_locked,
                    is_segment_archived, is_segment_previously_published, replace_block, replace_segment)
from .mixins import MasterSyllabusLockedAccessMixin
from core.views.funcs import get_cbv_context, get_environs, get_modal
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import AccessMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import DeleteView, DetailView, TemplateView, UpdateView, View
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin


class BlockAccessMixin(MasterSyllabusLockedAccessMixin, AccessMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        archived = is_block_archived(self.kwargs['pk'])
        locked = is_master_syllabus_locked(self.kwargs['master_syllabus_id'])
        published = is_block_previously_published(self.kwargs['pk'], self.kwargs['master_syllabus_id'])
        if archived:
            self.type = 'n archived'
            return self.handle_no_permission()
        elif locked or published:
            self.type = ' locked'
            return self.handle_no_permission()
        else:
            return super(BlockAccessMixin, self).dispatch(request, *args, **kwargs)

    def get_permission_denied_message(self):
        self.permission_denied_message = 'This block is associated with a' + self.type + \
                                         ' master syllabus, so it cannot be modified or deleted.'
        return self.permission_denied_message


class BlockContextMixin(ContextMixin, View):
    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super(BlockContextMixin, self).get_context_data(**kwargs)
        bond = Bond.objects.get(segment_id=self.kwargs['segment_id'], block=self.object)
        master_syllabus = MasterSyllabus.objects.get(pk=self.kwargs['master_syllabus_id'])
        context['bond'] = bond
        context['bonds'] = Bond.objects.filter(segment_id=self.kwargs['segment_id'])
        context['master_bond'] = MasterBond.objects.get(master_syllabus_id=self.kwargs['master_syllabus_id'],
                                                        segment_id=self.kwargs['segment_id'])
        context['master_syllabus'] = master_syllabus
        context['render_mode'] = 'view'
        context['term'] = master_syllabus.term
        return {**context, **environs}


class BlockFormMixin(FormMixin, View):
    def get_form_kwargs(self):
        kwargs = super(BlockFormMixin, self).get_form_kwargs()
        kwargs.update({'segment_id': self.kwargs['segment_id']})
        return kwargs

    def get_success_url(self):
        return reverse('editor:mastersyllabus:segment:detail', args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],))


class BlockCreateMixin(PermissionRequiredMixin, MasterSyllabusLockedAccessMixin, BlockFormMixin, FormMixin, View):
    permission_required = 'editor.add_block'

    def form_valid(self, form):
        master_syllabus = MasterSyllabus.objects.get(pk=self.kwargs['master_syllabus_id'])
        form.instance.effective_term = master_syllabus.term
        form.instance.type = self.extra_context['type']
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:block:' + self.extra_context['type'] + ':create',
                                     args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],))
        if is_segment_archived(self.kwargs['segment_id']) or \
                is_segment_previously_published(self.kwargs['segment_id'], self.kwargs['master_syllabus_id']):
            context['callback'] = 'done_load_regions_replace'
        else:
            context['callback'] = 'done_reload_segment'
        context['master_bond'] = MasterBond.objects.get(master_syllabus_id=self.kwargs['master_syllabus_id'],
                                                        segment_id=self.kwargs['segment_id'])
        if self.extra_context['expanded']:
            context['target'] = '.offcanvas-full-container'
        else:
            context['target'] = '#content-container'
        return {**context, **environs}

    def get_success_url(self):
        max_order = Bond.objects.filter(segment_id=self.kwargs['segment_id']).order_by('-order').first()
        order = (max_order.order if max_order else 0)
        bond = Bond(segment_id=self.kwargs['segment_id'], block_id=self.object.id, order=(order + 10),
                    owner=self.request.user)
        bond.save()
        if self.extra_context['expanded'] and not self.extra_context['type'] == 'multiple_choice_question':
            return reverse('editor:block:' + self.extra_context['type'] + ':update',
                           args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'], self.object.id,))
        else:
            return reverse('editor:mastersyllabus:segment:detail', args=(self.kwargs['master_syllabus_id'],
                                                                        self.kwargs['segment_id'],))

    def get_template_names(self):
        if self.extra_context['expanded']:
            return ['editor/mastersyllabus/segment/block/card/add.html']
        return ['core/offcanvas/add.html']

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


class BlockUpdateMixin(PermissionRequiredMixin, MasterSyllabusLockedAccessMixin, BlockFormMixin, FormMixin, View):
    def form_valid(self, form):
        if hasattr(self.object, 'printableblock') and not form.instance.print_group:
            form.instance.print_group = None
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        master_syllabus = MasterSyllabus.objects.get(pk=self.kwargs['master_syllabus_id'])
        if is_segment_archived(self.kwargs['segment_id']) or \
                is_segment_previously_published(self.kwargs['segment_id'], self.kwargs['master_syllabus_id']) or \
                is_addendum_necessary(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'], self.kwargs['pk']):
            context['callback'] = 'done_load_regions_replace'
        else:
            context['callback'] = 'done_close_full'
        context['delete_url'] = reverse('editor:block:delete', args=(self.kwargs['master_syllabus_id'],
                                                                    self.kwargs['segment_id'], self.object.id,))
        context['term'] = master_syllabus.term
        if self.extra_context['expanded']:
            context['bond'] = Bond.objects.get(segment_id=self.kwargs['segment_id'], block_id=self.object.id)
            context['edit_url'] = reverse('editor:block:' + self.object.type + ':update',
                                          args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                self.object.id,))
            context['master_syllabus'] = MasterSyllabus.objects.get(pk=self.kwargs['master_syllabus_id'])
        else:
            context['edit_url'] = reverse('editor:block:' + self.object.type + ':update',
                                          args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                self.object.id,))
        if ((is_block_archived(self.kwargs['pk']) or
             is_block_previously_published(self.kwargs['pk'], self.kwargs['master_syllabus_id'])) and
                ((self.object.type == 'details') or (self.object.type == 'list') or (self.object.type == 'schedule') or
                 (self.object.type == 'table'))):
            context['render_mode'] = 'replace'
        else:
            context['render_mode'] = 'edit'
        context['target'] = '#content-container'
        return {**context, **environs}

    def get_success_url(self):
        return reverse('editor:mastersyllabus:segment:detail', args=(self.kwargs['master_syllabus_id'],
                                                                    self.kwargs['segment_id'],))

    def get_template_names(self):
        if self.extra_context['expanded']:
            return ['editor/mastersyllabus/segment/block/card/edit.html']
        return ['core/offcanvas/edit.html']

    def has_permission(self):
        if self.request.user.has_perm('editor.change_block') or self.request.user.has_perm('editor.delete_block'):
            return True
        return False

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            if is_segment_archived(self.kwargs['segment_id']) or \
                    is_segment_previously_published(self.kwargs['segment_id'], self.kwargs['master_syllabus_id']):
                self.kwargs['segment_id'] = replace_segment(request, self.kwargs['master_syllabus_id'],
                                                            self.kwargs['segment_id'])
            if is_addendum_necessary(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'], self.kwargs['pk']):
                self.object = replace_block(request, self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                            self.object, self.object.type)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class BlockBatchView(PermissionRequiredMixin, TemplateView):
    permission_required = ('editor.change_block',)
    template_name = 'editor/mastersyllabus/segment/options/batch.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['blocks'] = Block.objects.filter(bond__segment_id=self.kwargs['segment_id']).order_by('bond__order')
        context['callback'] = 'done_close_full'
        context['master_syllabus_id'] = self.kwargs['master_syllabus_id']
        context['segment_id'] = self.kwargs['segment_id']
        context['target'] = '#content-container'
        return {**context, **environs}

    def get_success_url(self):
        return reverse('editor:mastersyllabus:segment:detail', args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],))


class BlockDeleteView(PermissionRequiredMixin, FormInvalidMixin, BlockAccessMixin, DeleteViewFormMixin, DeleteView):
    permission_required = ('editor.delete_block',)
    model = Block
    form_class = BlockForm

    def form_valid(self, form):
        if self.object.type == 'schedule':
            Schedule.objects.get(pk=self.object.printableblock.scheduleblock.schedule.id).delete()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['callback'] = 'done_close_full'
        context['modal']['target'] = '#content-container'
        context['modal']['url'] = reverse('editor:block:delete', args=(self.kwargs['master_syllabus_id'],
                                                                      self.kwargs['segment_id'], self.object.id,))
        return context

    def get_success_url(self):
        return reverse('editor:mastersyllabus:segment:detail', args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],))


class BlockDetailView(PermissionRequiredMixin, BlockContextMixin, DetailView):
    model = Block

    def get_template_names(self):
        return['editor/mastersyllabus/segment/block/card/card.html']

    def has_permission(self):
        if self.request.user.has_perm('editor.change_block') or self.request.user.has_perm('editor.delete_block'):
            return True
        return False


class PrintableBlockPublishView(PermissionRequiredMixin, MasterSyllabusLockedAccessMixin, FormInvalidMixin, UpdateView):
    permission_required = ('editor.change_block',)
    model = PrintableBlock
    form_class = PrintableBlockPublishForm
    template_name = 'editor/helpers/modal/generic.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        message = '<strong>WARNING</strong>: '
        if self.object.published:
            message += 'revoking this block makes it unavailable via a direct URL. If you\'ve previously published ' \
                       'this block and shared the direct URL, it will no longer work.'
        else:
            message += 'publishing this block makes it available via a direct URL (without the need of publishing a ' \
                       'syllabus).'
        context['modal'] = get_modal(message, message_alert_css='m-0', message_type='warning',
                                     operation=('revoked' if self.object.published else 'published'),
                                     target='#segment-' + str(self.kwargs['segment_id']) + '-block-' +
                                            str(self.object.id) + '-content',
                                     submit_icon=('cloud-minus' if self.object.published else 'cloud-plus'),
                                     submit_text=('Revoke' if self.object.published else 'Publish'),
                                     url=reverse('editor:block:publish', args=(self.kwargs['master_syllabus_id'],
                                                                              self.kwargs['segment_id'],
                                                                              self.object.id,)))
        context['verbose_name'] = 'block'
        return {**context, **environs}

    def get_success_url(self):
        return reverse('editor:block:detail', args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                   self.object.id,))

    def form_valid(self, form):
        form.instance.published = not bool(self.object.published)
        if form.instance.published:
            permalink = form.instance.name.replace(' ', '_').lower()
            blocks = Block.objects.filter(printableblock__permalink=permalink).order_by('printableblock__permalink')
            if blocks.count() == 0:
                form.instance.permalink = permalink
            else:
                last_block = blocks.last()
                if last_block.printableblock.permalink:
                    block = last_block.printableblock.permalink.split('__')
                    try:
                        permalink += '__' + str(int(block[1]) + 1)
                    except Exception:
                        permalink += '__1'
                    form.instance.permalink = permalink
        return super().form_valid(form)

from core.forms import ArrangeForm
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, FormView, UpdateView, View
from django.views.generic.edit import FormMixin
from editor.forms.blocks.details import *


class DetailsBlockDetailFormMixin(FormMixin, View):
    def get_success_url(self):
        return reverse('editor:block:details:update', args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                           self.kwargs['block_id'],))


class DetailsBlockDetailArrangeView(PermissionRequiredMixin, FormInvalidMixin, DetailsBlockDetailFormMixin, FormView):
    form_class = ArrangeForm
    template_name = 'editor/helpers/modal/arrange.html'

    def form_valid(self, form):
        order = 10
        ordering = form.cleaned_data['ordering'].split('|')
        for detail_id in ordering:
            item = DetailsBlockDetail.objects.get(pk=detail_id)
            item.order = order
            item.save()
            order += 10
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['modal'] = {}
        context['modal']['items'] = (DetailsBlockDetail.objects
                                     .filter(details_block_id=self.kwargs['block_id'])
                                     .values('id', name=models.F('summary'))
                                     .order_by('order'))
        context['modal']['message'] = '<strong>NOTE</strong>: to rearrange the details on this detail block, first ' \
                                      'select a detail from the list below, then use the up and down arrow buttons ' \
                                      'to reorder the details, and then click the Save button to save your changes.'
        context['modal']['message_type'] = 'info'
        context['modal']['model'] = 'details'
        context['modal']['target'] = '.offcanvas-full-container'
        context['modal']['url'] = reverse('editor:block:details:detail:arrange',
                                          args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                self.kwargs['block_id'],))
        return {**context, **environs}

    def has_permission(self):
        if self.request.user.has_perm('editor.change_detailsblockdetail'):
            return True
        return False


class DetailsBlockDetailCreateView(PermissionRequiredMixin, FormInvalidMixin, DetailsBlockDetailFormMixin, CreateView):
    permission_required = 'editor.add_detailsblockdetail'
    model = DetailsBlockDetail
    form_class = DetailsBlockDetailForm
    template_name = 'core/offcanvas/add.html'

    def form_valid(self, form):
        details = DetailsBlockDetail.objects.filter(details_block_id=self.kwargs['block_id']).last()
        if details:
            form.instance.order = details.order + 10
        else:
            form.instance.order = 10
        form.instance.details_block = DetailsBlock.objects.get(pk=self.kwargs['block_id'])
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:block:details:detail:create', args=(self.kwargs['master_syllabus_id'],
                                                                                self.kwargs['segment_id'],
                                                                                self.kwargs['block_id'],))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}


class DetailsBlockDetailDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin,
                                   DetailsBlockDetailFormMixin, DeleteView):
    permission_required = 'editor.delete_detailsblockdetail'
    model = DetailsBlockDetail
    form_class = DetailsBlockDetailDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['target'] = '.offcanvas-full-container'
        context['modal']['url'] = reverse('editor:block:details:detail:delete',
                                          args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                self.kwargs['block_id'], self.object.id,))
        return context


class DetailsBlockDetailUpdateView(PermissionRequiredMixin, FormInvalidMixin, DetailsBlockDetailFormMixin, UpdateView):
    model = DetailsBlockDetail
    form_class = DetailsBlockDetailForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = reverse('editor:block:details:detail:delete',
                                        args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                              self.kwargs['block_id'], self.object.id,))
        context['edit_url'] = reverse('editor:block:details:detail:update',
                                      args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                            self.kwargs['block_id'], self.object.id))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}

    def has_permission(self):
        if self.request.user.has_perm('editor.change_detailsblockdetail') or \
                self.request.user.has_perm('editor.delete_detailsblockdetail'):
            return True
        return False

from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView, View
from django.views.generic.edit import FormMixin
from editor.forms.blocks.table import *


class TableBlockRowFormMixin(FormMixin, View):
    def get_success_url(self):
        return reverse('editor:block:table:update', args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                         self.kwargs['block_id'],))


class TableBlockRowCreateView(PermissionRequiredMixin, FormInvalidMixin, TableBlockRowFormMixin, CreateView):
    permission_required = 'editor.add_tableblockrow'
    model = TableBlockRow
    form_class = TableBlockRowForm
    template_name = 'core/offcanvas/add.html'

    def form_valid(self, form):
        table = TableBlock.objects.get(pk=self.kwargs['block_id'])
        form.instance.table = table
        form.instance.owner = self.request.user
        result = super().form_valid(form)
        for col in range(table.number_of_columns):
            cell = TableBlockCell(table_row=self.object, column_number=col, owner=self.request.user)
            cell.save()
        return result

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:block:table:row:create', args=(self.kwargs['master_syllabus_id'],
                                                                           self.kwargs['segment_id'],
                                                                           self.kwargs['block_id'],))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}


class TableBlockRowDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin,
                              TableBlockRowFormMixin, DeleteView):
    permission_required = 'editor.delete_tableblockrow'
    model = TableBlockRow
    form_class = TableBlockRowDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['target'] = '.offcanvas-full-container'
        context['modal']['url'] = reverse('editor:block:table:row:delete', args=(self.kwargs['master_syllabus_id'],
                                                                                self.kwargs['segment_id'],
                                                                                self.kwargs['block_id'],
                                                                                self.object.id,))
        return context


class TableBlockRowUpdateView(PermissionRequiredMixin, FormInvalidMixin, TableBlockRowFormMixin, UpdateView):
    model = TableBlockRow
    form_class = TableBlockRowForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = reverse('editor:block:table:row:delete', args=(self.kwargs['master_syllabus_id'],
                                                                              self.kwargs['segment_id'],
                                                                              self.kwargs['block_id'],
                                                                              self.object.id,))
        context['edit_url'] = reverse('editor:block:table:row:update', args=(self.kwargs['master_syllabus_id'],
                                                                            self.kwargs['segment_id'],
                                                                            self.kwargs['block_id'],
                                                                            self.object.id))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}

    def has_permission(self):
        if self.request.user.has_perm('editor.change_tableblockrow') or \
                self.request.user.has_perm('editor.delete_tableblockrow'):
            return True
        return False

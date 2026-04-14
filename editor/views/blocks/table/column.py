from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import UpdateView, View
from django.views.generic.edit import FormMixin
from editor.forms.blocks.table import *


class TableBlockColumnFormMixin(FormMixin, View):
    def get_success_url(self):
        return reverse('editor:block:table:update', args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                         self.kwargs['block_id'],))


class TableBlockColumnUpdateView(PermissionRequiredMixin, FormInvalidMixin, TableBlockColumnFormMixin, UpdateView):
    model = TableBlockColumn
    form_class = TableBlockColumnForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = False
        context['edit_url'] = reverse('editor:block:table:column:update', args=(self.kwargs['master_syllabus_id'],
                                                                               self.kwargs['segment_id'],
                                                                               self.kwargs['block_id'],
                                                                               self.object.id))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}

    def has_permission(self):
        if self.request.user.has_perm('editor.change_tableblockcol') or \
                self.request.user.has_perm('editor.delete_tableblockcol'):
            return True
        return False

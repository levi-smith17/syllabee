from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import FormInvalidMixin
from django.urls import reverse
from django.views.generic import CreateView, UpdateView
from editor.views.block import BlockCreateMixin, BlockUpdateMixin
from editor.forms.blocks.table import *


class TableBlockCreateView(BlockCreateMixin, FormInvalidMixin, CreateView):
    model = TableBlock
    form_class = TableBlockCreateForm

    def form_valid(self, form):
        result = super().form_valid(form)
        for col in range(self.object.number_of_columns):
            column = TableBlockColumn(table=self.object, column_number=col, owner=self.request.user)
            column.save()
        return result


class TableBlockUpdateView(BlockUpdateMixin, FormInvalidMixin, UpdateView):
    model = TableBlock
    form_class = TableBlockForm

    def form_valid(self, form):
        rows = TableBlockRow.objects.filter(table=self.object)
        if rows.count() > 0:
            for row in rows:
                column_count = TableBlockCell.objects.filter(table_row=row).count()
                difference = (self.object.number_of_columns - column_count)
                if difference > 0:  # We added more columns, so add additional cells to each existing row.
                    for col in range(column_count, self.object.number_of_columns):
                        cell = TableBlockCell(table_row=row, column_number=col, owner=self.request.user)
                        cell.save()
                elif difference < 0:  # We decreased the number of columns. Do nothing (for now).
                    break
                else:  # We didn't add or remove columns. No action required.
                    break
        # Update all cells
        cells = TableBlockCell.objects.filter(table_row__table=self.object, table_row__table__number_of_columns__gt=0)
        if cells.count() > 0:
            for cell in cells:
                if ('cell_' + str(cell.id)) in self.request.POST:
                    cell.value = self.request.POST.get('cell_' + str(cell.id), '')
                cell.save()
        return super().form_valid(form)


class TableBlockPropertiesUpdateView(BlockUpdateMixin, FormInvalidMixin, UpdateView):
    permission_required = 'editor.change_tableblock'
    model = TableBlock
    form_class = TableBlockPropertiesForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = False
        context['edit_url'] = reverse('editor:block:table:update_properties',
                                      args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                            self.object.id,))
        context['edit_message'] = {'alert_css': 'm-0', 'icon': '',
                                   'text': '<strong>WARNING</strong>: saving table block properties will reload the '
                                           'table (on the previous screen), potentially resulting in data loss. Make '
                                           'sure that all table changes are saved before saving table block '
                                           'properties.',
                                   'text_css': '', 'type': 'warning'}
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}

    def get_success_url(self):
        return reverse('editor:block:table:update', args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                         self.kwargs['pk'],))

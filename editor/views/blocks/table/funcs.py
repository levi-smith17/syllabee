from core.views.buttons import render_edit_button
from editor.models import *


def render_table(request, table, render_mode='view', *args):
    """
    Renders this TableBlock based on the provided render mode.

    Parameters:
    :param (Request) request:       The request object (for session variables).
    :param (TableBlock) table:      The TableBlock to render.
    :param (string) render_mode:    Determines how to render this table. Options are 'edit', 'view', or 'print'.

    Returns:
    :return (string)                - Returns HTML containing a properly formatted table.
    """
    html = '<table class="table' + table.accent + table.borders + ' m-0' + \
           (' table-bordered border-secondary' if render_mode == 'edit' else ' border-light') + '">'
    if table.caption:
        html += '<caption' + ((' style="caption-side: ' + table.caption_position) if table.caption_position else '') + \
                '" class="text-white">' + table.caption + '</caption>'
    columns = TableBlockColumn.objects.filter(table=table)
    if columns.count() > 0:
        html += '<colgroup>'
        if render_mode == 'edit':
            html += '<col>'
        for column in columns:
            html += '<col style="' + str(column.style) + '">'
        html += '</colgroup>'
    if render_mode == 'edit' and request.user.has_perm('editor.add_tableblockcolumn'):
        html += '<thead>'
        html += '<tr class="text-bg-warning">'
        html += '<th class="text-bg-warning">&nbsp;</th>'
        columns = (TableBlockColumn.objects
                   .filter(table=table, column_number__lt=table.number_of_columns)
                   .order_by('column_number'))
        for column in columns:
            html += '<th class="align-middle p-1 text-bg-warning">'
            html += render_edit_button('Column', 'editor:block:table:column:update', *(list(args) + [column.id]))
            html += '</th>'
        html += '</tr>'
        html += '</thead>'
    html += render_table_section(request, table, 'head', render_mode, *args)
    html += render_table_section(request, table, 'body', render_mode, *args)
    html += render_table_section(request, table, 'foot', render_mode, *args)
    html += '</table>'
    return html


def render_table_section(request, table, section_type, render_mode='view', *args):
    """
    Renders this TableBlock based on the provided render mode.

    Parameters:
    :param (Request) request:       The request object (for session variables).
    :param (TableBlock) table:      The TableBlock to render.
    :param (str) section_type:      The type of section to render. Options are 'head', 'body', or 'foot'.
    :param (str) render_mode:       Determines how to render this table. Options are 'edit', 'view', or 'print'.

    Returns:
    :return (string)                - Returns HTML containing a properly formatted table.
    """
    html = ''
    rows = TableBlockRow.objects.filter(table=table, type=section_type)
    if rows.count() > 0:
        html += '<t' + section_type + '>'
        for row in rows:
            if render_mode == 'edit' and request.user.has_perm('editor.change_tableblockrow'):
                if section_type == 'head':
                    color = ' text-bg-warning'
                elif section_type == 'foot':
                    color = ' text-bg-info'
                else:
                    color = ' text-bg-dark'
            else:
                color = ' text-bg-dark'
            html += '<tr class="' + color + '">'
            if render_mode == 'edit' and request.user.has_perm('editor.change_tableblockrow'):
                html += '<th class="text-bg-warning align-middle p-1">'
                html += render_edit_button('Row', 'editor:block:table:row:update', *(list(args) + [row.id]))
                html += '</th>'
            cells = TableBlockCell.objects.filter(table_row=row, column_number__lt=table.number_of_columns)
            for cell in cells:
                column = TableBlockColumn.objects.get(table=table, column_number=cell.column_number)
                cell_type = 'th' if section_type == 'head' else 'td'
                html += '<' + cell_type + ' rowspan="' + str(cell.rowspan) + '" colspan="' + str(cell.colspan) + '"'
                if render_mode == 'edit' and request.user.has_perm('editor.change_tableblockcell'):
                    html += ' class="p-0"'
                html += ' style="' + column.style + '">'
                if render_mode == 'edit' and request.user.has_perm('editor.change_tableblockcell'):
                    html += '<div class="d-flex">'
                    element_id = 'table-' + str(table.id) + '-row-' + str(row.id) + '-cell-' + str(cell.id)
                    html += '<input type="text" id="' + element_id + \
                            '" name="cell_' + str(cell.id) + '" value="' + (cell.value if cell.value else '') + \
                            '" class="form-control ' + color + ' border-0 rounded-0 h-3r">'
                    html += '</div>'
                else:
                    html += (cell.value if cell.value else '')
                html += '</' + cell_type + '>'
            html += '</tr>'
        html += '</' + section_type + '>'
    return html

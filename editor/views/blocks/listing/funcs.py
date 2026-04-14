from core.views.buttons import render_edit_button
from editor.models import *


def render_list(request, list_block, render_mode='view', *args):
    """
    Retrieves the content of the requested details block.

    Parameters:
    :param (Request) request:               The request object (for session variables).
    :param (ListBlock) list_block:          The list block object to be rendered.
    :param (string) render_mode:            Determines how to render this list content. Options are 'edit', 'view',
                                            or 'print'.

    Returns:
    :return (string)                        - Returns HTML containing a properly formatted list block.
    """
    html = '<div class="d-grid gap-2">'
    html += render_list_children(request, list_block, None, '', render_mode, True, *args)
    html += '</div>'
    return html


def render_list_children(request, list_block, list_item, html, render_mode, initial, *args):
    """
    Retrieves the children of a list item recursively (if any).

    Parameters:
    :param (Request) request:               The request object (for session variables).
    :param (ListBlock) list_block:          The list block object to be rendered.
    :param (ListBlockItem) list_item:       The list item to retrieve children for.
    :param (string) html:                   The HTML being generated of a list item's children.
    :param (string) render_mode:            Determines how to render this list content. Options are 'edit', 'view',
                                            or 'print'.
    :param (Boolean) initial:               Determines whether this is the initial call of this function or not.

    Returns:
    :return (string)                        - Returns HTML containing a properly formatted list item's children.
    """
    if initial:
        child_items = ListBlockItem.objects.filter(list_block=list_block, parent_item__isnull=True)
    else:
        child_items = ListBlockItem.objects.filter(list_block=list_block, parent_item=list_item)
    if child_items.count() > 0:
        if list_block.list_type == 'Ordered':
            html += '<ol' + ((' start="' + str(list_block.ordered_start) + '"') if list_block.ordered_start else '') + \
                    ' type="' + str(list_block.ordered_type) + '" class="d-flex flex-column gap-1">'
        else:
            html += '<ul class="d-flex flex-column gap-1">'
        for child_item in child_items:
            html += '<li>'
            html += '<div class="d-flex align-items-start gap-2">'
            if render_mode == 'edit':
                html += '<div>'
                if request.user.has_perm('editor.change_listblockitem') or \
                        request.user.has_perm('editor.delete_listblockitem'):
                    html += render_edit_button('Item', 'editor:block:list:item:update', *args, list_block.id,
                                               child_item.id)
                html += '</div>'
            html += '<div>'
            html += child_item.content + render_list_children(request, list_block, child_item, '', render_mode, False,
                                                              *args)
            html += '</div>'
            html += '</div>'
            html += '</li>'
        if list_block.list_type == 'Ordered':
            html += '</ol>'
        else:
            html += '</ul>'
        return html
    else:
        return ''

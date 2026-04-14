from core.views.buttons import render_edit_button
from editor.models import DetailsBlockDetail


def render_details(request, details_block, render_mode='view', *args):
    """
    Retrieves the content of the requested details block.

    Parameters:
    :param (Request) request:               The request object (for session variables).
    :param (DetailsBlock) details_block:    The details block object to be rendered.
    :param (string) render_mode:            Determines how to render this details content. Options are 'edit', 'view',
                                            or 'print'.

    Returns:
    :return (string)                        - Returns HTML containing a properly formatted details block.
    """
    html = '<div class="d-grid gap-2">'
    html += '<span>Click on a question or statement below to view more details.</span>'
    detail_elements = DetailsBlockDetail.objects.filter(details_block=details_block)
    for detail in detail_elements:
        html += '<div class="d-flex gap-3">'
        if render_mode == 'edit':
            if request.user.has_perm('editor.change_detailsblockdetail') or \
                    request.user.has_perm('editor.delete_detailsblockdetail'):
                html += render_edit_button('Detail', 'editor:block:details:detail:update', *args, details_block.id,
                                            detail.id)
        html += '<details' + (' open' if render_mode == 'print' else '') + '>'
        html += '<summary>' + detail.summary + '</summary>'
        html += detail.content
        html += '</details>'
        html += '</div>'
    html += '</div>'
    return html

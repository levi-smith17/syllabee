from django.db.models import Sum
from editor.models import GradingScaleGrade, ScheduleTopic


def render_grade_determination(request, gdb, render_mode='view'):
    """
    Retrieves the body of the requested grade determination block.

    Parameters:
    :param (Request) request:               The request object (for session variables).
    :param (GradeDeterminationBlock) gdb:   The grade determination block to render.
    :param (string) render_mode:            Determines how to render this grade determination block. Options are 'view'
                                            or 'print'.

    Returns:
    :return (string)                        - Returns HTML containing a properly formatted grade determination block.
    """
    html = ('<p class="card-text">' + gdb.description + '</p>' if gdb.description else '')
    html += '<div class="d-flex flex-column flex-md-row gap-3">'
    html += render_points_breakdown(request, gdb, render_mode)
    html += render_grading_breakdown(request, gdb, render_mode)
    html += '</div>'
    return html


def render_points_breakdown(request, gdb, render_mode):
    """
    Retrieves the point breakdown portion of a grade determination block.

    Parameters:
    :param (Request) request:               The request object (for session variables).
    :param (GradeDeterminationBlock) gdb:   The grade determination to retrieve a point breakdown for.
    :param (string) render_mode:            Determines how to render this grade determination block. Options are 'view'
                                            or 'print'.

    Returns:
    :return (string)                        - Returns HTML containing a properly formatted points breakdown.
    """
    html = ''
    if gdb.schedule:
        html = '<table class="table table-bordered m-0 text-bg-dark">'
        html += '<thead>'
        html += '<tr><th colspan="2">'
        html += '<div class="d-flex justify-content-between align-items-center">Points Breakdown'
        html += '</div>'
        html += '</th></tr>'
        html += '</thead>'
        html += '<tbody>'
        total_points = 0
        topics = (ScheduleTopic.objects
                  .filter(unit__schedule=gdb.schedule.schedule, assignment_points__gt=0)
                  .values('assignment_category')
                  .order_by('assignment_category')
                  .annotate(category_points=Sum('assignment_points')))
        if topics:
            for topic in topics:
                html += '<tr>'
                html += '<td>' + str(topic['assignment_category']) + '</td>'
                html += '<td>' + str(topic['category_points']) + 'pts</td>'
                html += '</tr>'
                total_points += topic['category_points']
        html += '<tr>'
        html += '<td>Total</td>'
        html += '<td>' + str(total_points) + 'pts</td>'
        html += '</tr>'
        html += '</tbody>'
        html += '</table>'
    return html


def render_grading_breakdown(request, gdb, render_mode):
    """
    Retrieves the grading breakdown portion of a grade determination block.

    Parameters:
    :param (Request) request:               The request object (for session variables).
    :param (GradeDeterminationBlock) gdb:   The grade determination block to retrieve a grading breakdown for.
    :param (string) render_mode:            Determines how to render this grade determination block. Options are 'view'
                                            or 'print'.

    Returns:
    :return (string)                        - Returns HTML containing a properly formatted grading breakdown.
    """
    html = '<table class="table table-bordered m-0 text-bg-dark">'
    html += '<thead>'
    html += '<tr><th colspan="' + str(3 if gdb.schedule else 2) + '">'
    html += '<div class="d-flex justify-content-between align-items-center">Grading Breakdown'
    html += '</div>'
    html += '</th></tr>'
    html += '</thead>'
    html += '<tbody>'
    grades = GradingScaleGrade.objects.filter(grading_scale=gdb.grading_scale)
    for grade in grades:
        html += '<tr>'
        html += '<td>' + str(grade.percent_start) + ' - ' + str(grade.percent_end) + '%</td>'
        if gdb.schedule:
            topics = ScheduleTopic.objects.filter(unit__schedule=gdb.schedule.schedule)
            total = 0
            if topics:
                for topic in topics:
                    total += topic.assignment_points
            html += '<td>' + str(round(grade.percent_start / 100 * total)) + 'pts - ' + \
                    str(round(grade.percent_end / 100 * total)) + 'pts</td>'
        html += '<td>' + grade.letter + '</td>'
        html += '</tr>'
    html += '</tbody>'
    html += '</table>'
    return html

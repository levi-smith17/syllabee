import re
from core.views.buttons import render_add_button, render_copy_button, render_edit_button
from editor.models import *


def correct_unit_across_breakpoint(request, schedule, html, term, render_mode, **override_kwargs):
    """
    Corrects the HTML so a unit doesn't span a midpoint break if a midpoint break exists for this schedule.

    Parameters:
    :param (Request) request:       The request object (for session variables).
    :param (Schedule) schedule:     The schedule to sanitize.
    :param (str) html:              A string containing the HTML to sanitize.
    :param (Term) term:             The term to sanitize weeks within.
    :param (string) render_mode:    Determines how to render this schedule. Options are 'edit', 'options', 'view', or
                                    'print'.

    Returns:
    :return (string)                - Returns a string of corrected HTML.
    """
    if term.has_midpoint_break:
        midpoint_break = term.length.num_weeks / 2
        topics_beyond_break = ScheduleTopic.objects.filter(unit__schedule=schedule, week__gt=midpoint_break)
        if topics_beyond_break.count() > 0:
            units = ScheduleUnit.objects.filter(schedule=schedule)
            for unit in units:
                num_weeks_in_unit = ScheduleTopic.objects.filter(unit=unit).values('week').distinct().count()
                if unit.week <= midpoint_break < (unit.week + num_weeks_in_unit):
                    delimiter = 'Week of <strong>Midpoint Break</strong>'
                    temp_html = html.split(delimiter)
                    temp_html[1] = temp_html[1].replace(unit.name, unit.name + ' (cont.)')
                    unit.name = unit.name + ' (cont.)'
                    pattern = render_unit_cell(request, schedule, unit, render_mode, **override_kwargs)
                    num_occurrences = len(re.findall(re.escape(pattern), temp_html[1]))
                    html = temp_html[0] + delimiter + sanitize_cell(temp_html[1], pattern, num_occurrences)
    return html


def render_due_date(schedule, current_date, topic):
    """
    Determines a due date based on the current_date and associated topic and returns it.

    Parameters:
    :param (Schedule) schedule:     The schedule being referenced.
    :param (DateTime) current_date: The date used to calculate the due date.
    :param (Topic) topic:           The topic being used to calculate the correct due date.

    Returns:
    :return (string)                - Returns HTML containing a properly formatted due date.
    """
    if schedule.term_length.num_weeks == topic.week:
        # Finals Week
        days = (DAYS_OF_THE_WEEK.index((schedule.finals_due_day, schedule.finals_due_day)) - 1)
    else:
        days = (DAYS_OF_THE_WEEK.index((schedule.assignment_due_day, schedule.assignment_due_day)) + 6)
    return (current_date + datetime.timedelta(days=days)).strftime("%m/%d/%Y")


def render_schedule(request, schedule, term, render_mode='view', **override_kwargs):
    """
    Retrieves the body of the requested schedule (by ID).

    Parameters:
    :param (Request) request:       The request object (for session variables).
    :param (Schedule) schedule:     The ID of the schedule to retrieve.
    :param (Term) term:             The term used to render the schedule correctly.
    :param (string) render_mode:    Determines how to render this schedule. Options are 'edit', 'options', 'view', or
                                    'print'.

    Returns:
    :return (string)                - Returns HTML containing a properly formatted schedule body.
    """
    topics = ScheduleTopic.objects.filter(unit__schedule=schedule)
    start_date = term.start_date
    display_midpoint = True
    master_section = None
    if override_kwargs:
        master_section = (MasterBondSection.objects
                          .filter(master_bond__master_syllabus_id=override_kwargs['master_syllabus_id'],
                                  master_bond__segment_id=override_kwargs['segment_id'],
                                  section__isnull=False).first())
        override_kwargs['master_section'] = master_section
    html = '<p class="card-text">'
    html += schedule.description if schedule.description else ''
    html += ' <strong>All assignments are to be completed and submitted on ' + schedule.assignment_due_day + 's by ' + \
            schedule.assignment_due_time.strftime('%I:%M %p').lower() + ', unless otherwise noted</strong>!'
    html += '</p>'
    html += '<table class="table table-bordered d-none d-md-table d-lg-none d-xl-table m-0 text-bg-dark">'
    html += render_schedule_table_head(request, schedule, render_mode, **override_kwargs)
    html += '<tbody>'
    if topics:
        for topic in topics:
            if term.has_midpoint_break and topic.week >= ((term.length.num_weeks / 2) + 1):
                current_date = start_date + datetime.timedelta(days=(topic.week * 7))
                if display_midpoint:
                    midpoint_date = current_date - datetime.timedelta(days=7)
                    html += '<tr><td colspan="7">Week of <strong>Midpoint Break</strong> - ' + \
                            midpoint_date.strftime("%m/%d/%Y") + '</td></tr>'
                    display_midpoint = False
            else:
                current_date = start_date + datetime.timedelta(days=((topic.week - 1) * 7))
            html += '<tr>'
            # Weeks Column
            html += '<td>Week ' + str(topic.week).rjust(2, '0') + ' - ' + current_date.strftime("%m/%d/%Y") + '</td>'
            # Units Column
            if schedule.display_units_column:
                unit = ScheduleUnit.objects.get(pk=topic.unit.id)
                html += render_unit_cell(request, schedule, unit, render_mode, **override_kwargs)
            # Topics Column
            html += render_topic_cell(request, schedule, topic, render_mode, **override_kwargs)
            # Readings Column
            if topic.reading:
                html += '<td>' + topic.reading + '</td>'
            # Assignments Column
            html += '<td>'
            if topic.assignment_name:
                html += '<div class="d-flex justify-content-between"><span class="pe-2">'
                if topic.emphasize_assignment:
                    html += '<strong>'
                html += topic.assignment_name
                if topic.emphasize_assignment:
                    html += '</strong>'
                html += '</span>'
                if render_mode == 'options' and override_kwargs and (request.user.has_perm('editor.change_override') or
                                                                     request.user.has_perm('editor.delete_override')):
                    try:
                        override = Override.objects.filter(assignment=topic, section=master_section.section)
                        if override:
                            html += render_edit_button('Due Date Override', 'editor:block:schedule:override:update',
                                                       override_kwargs['master_syllabus_id'],
                                                       override_kwargs['segment_id'], override_kwargs['block_id'],
                                                       schedule.id, override[0].id)
                    except AttributeError:
                        pass
                html += '</div>'
                html += '</td>'
            else:
                html += 'N/A'
            html += '</td>'
            # Points Column
            html += '<td>'
            if topic.assignment_points > 0:
                html += str(topic.assignment_points) + ' pts'
            else:
                html += 'N/A'
            html += '</td>'
            # Due Dates Column
            override_count = 0
            try:
                override = Override.objects.get(assignment=topic, section=master_section.section)
                override_count = Override.objects.filter(section=master_section.section).count()
                due_date = override.due_date.strftime('%m/%d/%Y')
                if schedule.assignment_due_time != override.due_time:
                    due_date += ' @ ' + override.due_time.strftime('%I:%M %p')
            except (Override.DoesNotExist, AttributeError, KeyError):
                due_date = render_due_date(schedule, current_date, topic)
            html += '<td>'
            if override_kwargs:
                if override_count > 0:
                    html += due_date if topic.assignment_name else 'N/A'
                else:
                    html += due_date
            else:
                html += due_date
            html += '</td>'
            html += '</tr>'
    # Include Missing Unit Rows (if applicable)
    if schedule.display_units_column:
        units = ScheduleUnit.objects.filter(schedule=schedule)
        for unit in units:
            unit_cell = render_unit_cell(request, schedule, unit, render_mode, **override_kwargs)
            num_occurrences = len(re.findall(unit_cell, html))
            if num_occurrences == 0:
                current_date = start_date + datetime.timedelta(days=((unit.week - 1) * 7))
                html += '<tr>'
                # Weeks Column
                html += '<td>Week ' + str(unit.week).rjust(2, '0') + ' - ' + current_date.strftime("%m/%d/%Y") + '</td>'
                # Units Column
                html += unit_cell
                html += '<td colspan="5">&nbsp;</td>'
                html += '</tr>'
    html += '</tbody>'
    html += '</table>'
    html = sanitize_cells(request, schedule, html, term, render_mode, **override_kwargs)
    html += render_schedule_table_mobile(request, schedule, term, render_mode)
    return html


def render_schedule_table_head(request, schedule, render_mode, **override_kwargs):
    """
    Retrieves the table header of the requested schedule.

    Parameters:
    :param (Request) request:       The request object (for session variables).
    :param (Schedule) schedule:     The schedule to retrieve a header row for.
    :param (string) render_mode:    Determines how to render this schedule. Options are 'edit', 'options', 'view', or
                                    'print'.

    Returns:
    :return (string)                - Returns HTML containing a properly formatted schedule body.
    """
    html = '<thead>'
    html += '<tr>'
    html += '<th colspan="' + ('7' if schedule.display_units_column else '6') + '">Week-By-Week Breakdown'
    if request.user.has_perm('editor.change_schedule') or request.user.has_perm('editor.delete_schedule'):
        html += ' (<strong>' + str(schedule.term_length) + '</strong>)'
    html += '<div class="float-end">'
    html += '</div>'
    html += '</th>'
    html += '</tr>'
    html += '<tr>'
    html += '<th class="align-middle">Week #</th>'
    if schedule.display_units_column:
        html += '<th>'
        html += '<div class="d-flex justify-content-between align-items-center">Unit'
        if render_mode == 'edit' and request.user.has_perm('editor.add_scheduleunit'):
            html += render_add_button('Unit', 'editor:block:schedule:unit:create', override_kwargs['master_syllabus_id'],
                                    override_kwargs['segment_id'], override_kwargs['block_id'], schedule.id)
        html += '</div>'
        html += '</th>'
    html += '<th>'
    html += '<div class="d-flex justify-content-between align-items-center">Topic'
    if render_mode == 'edit' and request.user.has_perm('editor.add_scheduletopic'):
        html += render_add_button('Topic', 'editor:block:schedule:topic:create', override_kwargs['master_syllabus_id'],
                                  override_kwargs['segment_id'], override_kwargs['block_id'], schedule.id,)
    html += '</div>'
    html += '</th>'
    html += '<th class="align-middle">Reading</th>'
    html += '<th class="align-middle">'
    html += '<div class="d-flex justify-content-between align-items-center">Assignments'
    if render_mode == 'options' and override_kwargs and request.user.has_perm('editor.add_override'):
        html += render_add_button('Due Date Override', 'editor:block:schedule:override:create',
                                  override_kwargs['master_syllabus_id'], override_kwargs['segment_id'],
                                  override_kwargs['block_id'], schedule.id)
    html += '</div>'
    html += '</th>'
    html += '<th class="align-middle">Points</th>'
    html += '<th class="align-middle">Due Date</th>'
    html += '</tr>'
    html += '</thead>'
    return html


def render_schedule_table_mobile(request, schedule, term, render_mode):
    """
    Retrieves the body of the requested schedule (by ID).

    Parameters:
    :param (Request) request:       The request object (for session variables).
    :param (Schedule) schedule:     The schedule object used to generate the returned schedule.
    :param (Term) term:             The term to render this schedule for.
    :param (string) render_mode:    Determines how to render this schedule. Options are 'edit', 'options', 'view', or
                                    'print'.

    Returns:
    :return (string)                - Returns HTML containing a properly formatted schedule body.
    """
    current_date = term.start_date
    html = '<table class="table table-bordered mobile d-md-none d-lg-table d-xl-none m-0 text-bg-dark">'
    html += '<tbody>'
    for week in range(1, schedule.term_length.num_weeks + 1):
        html += '<tr>'
        # Weeks Row (Header)
        html += '<th colspan="2">'
        html += '<h5 class="m-0 mt-2">'
        html += 'Week ' + str(week).rjust(2, '0') + ' - ' + current_date.strftime('%m/%d/%Y')
        html += '</h5>'
        html += '</th>'
        html += '</tr>'
        # Unit(s) Row
        if schedule.display_units_column:
            html += '<tr>'
            unit_count = ScheduleUnit.objects.filter(schedule=schedule, week=week).count()
            html += '<th>Unit' + ('s' if unit_count != 1 else '') + '</th>'
            html += '<td>'
            units = ScheduleUnit.objects.filter(schedule=schedule, scheduletopic__week=week).distinct()
            if units.exists():
                for unit in units:
                    html += '<strong>Unit ' + str(unit.number).rjust(2, '0') + '</strong> - ' + unit.name + '<br>'
            else:
                html += 'N/A'
            html += '</td>'
            html += '</tr>'
        # Topic(s) Row
        html += '<tr>'
        topic_count = ScheduleTopic.objects.filter(week=week).count()
        html += '<th>Topic' + ('s' if topic_count != 1 else '') + '</th>'
        html += '<td>'
        topics = ScheduleTopic.objects.filter(unit__schedule=schedule, week=week)
        if topics.exists():
            for topic in topics:
                if topic.emphasize_topic:
                    html += '<strong>'
                if topic.number:
                    html += '<strong>Topic ' + str(topic.number).rjust(2, '0') + '</strong> - ' + topic.name
                else:
                    html += topic.name
                if topic.emphasize_topic:
                    html += '</strong>'
                html += '<br>'
        else:
            html += 'N/A'
        html += '</td>'
        html += '</tr>'
        # Reading(s) Row
        html += '<tr>'
        topic_count = ScheduleTopic.objects.filter(unit__schedule=schedule, week=week, reading__isnull=False).count()
        html += '<th>Reading' + ('s' if topic_count != 1 else '') + '</th>'
        html += '<td>'
        html += '<ol class="ps-3">'
        has_reading = False
        for topic in topics:
            if topic.reading:
                html += '<li>'
                if topic.number:
                    html += '<strong>Topic ' + str(topic.number).rjust(2, '0') + '</strong> Reading ' + topic.reading
                else:
                    html += topic.reading
                html += '<br>'
                html += '</li>'
                has_reading = True
        html += '</ol>'
        if not has_reading:
            html += 'N/A'
        html += '</td>'
        html += '</tr>'
        # Assignment(s) Row
        html += '<tr>'
        topic_count = ScheduleTopic.objects.filter(unit__schedule=schedule, week=week,
                                                   assignment_name__isnull=False).count()
        html += '<th>Asgmt' + ('s' if topic_count != 1 else '') + '</th>'
        html += '<td>'
        html += '<ol class="ps-3">'
        has_assignment = False
        for topic in topics:
            due_date = render_due_date(schedule, current_date, topic)
            if topic.assignment_name:
                html += '<li>'
                if topic.emphasize_assignment:
                    html += '<strong>'
                html += topic.assignment_name + ' (' + str(topic.assignment_points) + ' pts) (Due: ' + due_date + \
                        ')<br> '
                if topic.emphasize_assignment:
                    html += '</strong>'
                html += '</li>'
                has_assignment = True
        html += '</ol>'
        if not has_assignment:
            html += 'N/A'
        html += '</td>'
        html += '</tr>'
        if term.has_midpoint_break and week == (term.length.num_weeks / 2):
            current_date = current_date + datetime.timedelta(days=7)
            html += '<tr><td colspan="2">Week of <strong>Midpoint Break</strong> - ' + \
                    current_date.strftime("%m/%d/%Y") + '</td></tr>'
            current_date = current_date + datetime.timedelta(days=7)
        else:
            current_date = current_date + datetime.timedelta(days=7)
    html += '</tbody>'
    html += '</table>'
    return html


def render_topic_cell(request, schedule, topic, render_mode, **override_kwargs):
    """
    Retrieves an individual cell for a topic.

    Parameters:
    :param (Request) request:       The request object (for session variables).
    :param (Schedule) schedule:     A schedule object associated with this unit.
    :param (ScheduleTopic) topic:   The topic object to retrieve.
    :param (string) render_mode:    Determines how to render this schedule. Options are 'edit', 'options', 'view', or
                                    'print'.

    Returns:
    :return (string)                - Returns a string of sanitized HTML.
    """
    html = ''
    if topic.reading:
        html += '<td>'
    else:
        html += '<td colspan="2">'
    if topic.emphasize_topic:
        html += '<strong>'
    html += '<div class="d-flex justify-content-between"><span>'
    html += str(topic).replace('Topic', '<strong>Topic').replace(' - ', '</strong> - ')
    if topic.emphasize_topic:
        html += '</strong>'
    html += '</span>'
    if render_mode == 'edit' and (request.user.has_perm('editor.change_scheduletopic') or
                                  request.user.has_perm('editor.delete_scheduletopic')):
        html += '<span class="d-flex gap-1">'
        html += render_edit_button('Topic', 'editor:block:schedule:topic:update', override_kwargs['master_syllabus_id'],
                                   override_kwargs['segment_id'], override_kwargs['block_id'], schedule.id, topic.id)
        html += render_copy_button('Topic', 'editor:block:schedule:topic:copy', override_kwargs['master_syllabus_id'],
                                   override_kwargs['segment_id'], override_kwargs['block_id'], schedule.id, topic.id)
        html += '</span>'
    html += '</div>'
    html += '</td>'
    return html


def render_unit_cell(request, schedule, unit, render_mode, **override_kwargs):
    """
    Retrieves an individual cell for a unit.

    Parameters:
    :param (Request) request:       The request object (for session variables).
    :param (Schedule) schedule:     A schedule object associated with this unit.
    :param (ScheduleUnit) unit:     The unit object to retrieve.
    :param (string) render_mode:    Determines how to render this schedule. Options are 'edit', 'options', 'view', or
                                    'print'.

    Returns:
    :return (string)                - Returns a string of sanitized HTML.
    """
    html = '<td>'
    html += '<div class="d-flex justify-content-between">'
    html += '<span><strong>Unit ' + str(unit.number).rjust(2, '0') + '</strong> - ' + unit.name + '</span>'
    if render_mode == 'edit' and request.user.has_perm('editor.change_scheduleunit'):
        html += '<span class="d-flex gap-1">'
        html += render_edit_button('Unit', 'editor:block:schedule:unit:update', override_kwargs['master_syllabus_id'],
                                   override_kwargs['segment_id'], override_kwargs['block_id'], schedule.id, unit.id)
        if render_mode == 'edit' and request.user.has_perm('editor.add_scheduletopic'):
            html += render_add_button('Topic', 'editor:block:schedule:topic:create',
                                      override_kwargs['master_syllabus_id'], override_kwargs['segment_id'],
                                      override_kwargs['block_id'], schedule.id)
        html += '</span>'
    html += '</div>'
    html += '</td>'
    return html


def sanitize_cells(request, schedule, html, term, render_mode, **override_kwargs):
    """
    Removes duplicate cells and spans the first one over multiple rows.

    Parameters:
    :param (Request) request:       The request object (for session variables).
    :param (Schedule) schedule:     The schedule to sanitize.
    :param (str) html:              A string containing the HTML to sanitize.
    :param (Term) term:             The term to sanitize weeks within.
    :param (string) render_mode:    Determines how to render this schedule. Options are 'edit', 'options', 'view', or
                                    'print'.

    Returns:
    :return (string)                - Returns a string of sanitized HTML.
    """
    start_date = term.start_date
    current_date = start_date
    # Sanitize Weeks Column
    for week in range(1, schedule.term_length.num_weeks + 1):
        if term.has_midpoint_break and week == ((term.length.num_weeks / 2) + 1):
            current_date = start_date + datetime.timedelta(days=(week * 7))
        pattern = '<td>Week ' + str(week).rjust(2, '0') + ' - ' + current_date.strftime("%m/%d/%Y") + '</td>'
        num_occurrences = len(re.findall(re.escape(pattern), html))
        html = sanitize_cell(html, pattern, num_occurrences)
        current_date = current_date + datetime.timedelta(days=7)
    # Sanitize Units Column (if applicable)
    if schedule.display_units_column:
        if schedule.term_length.can_have_midpoint_break:
            html = correct_unit_across_breakpoint(request, schedule, html, term, render_mode, **override_kwargs)
        units = ScheduleUnit.objects.filter(schedule=schedule)
        for unit in units:
            pattern = render_unit_cell(request, schedule, unit, render_mode, **override_kwargs)
            num_occurrences = len(re.findall(re.escape(pattern), html))
            html = sanitize_cell(html, pattern, num_occurrences)
    # Sanitize Topics Column & Readings Column
    if render_mode != 'edit':
        topics = ScheduleTopic.objects.filter(unit__schedule=schedule)
        for topic in topics:
            pattern = render_topic_cell(request, schedule, topic, 'view', **override_kwargs)
            num_occurrences = len(re.findall(re.escape(pattern), html))
            html = sanitize_cell(html, pattern, num_occurrences)
            if topic.reading:
                pattern = '<td>' + topic.reading + '</td>'
                num_occurrences = len(re.findall(re.escape(pattern), html))
                html = sanitize_cell(html, pattern, num_occurrences)
    # Sanitize Due Dates Column
    override_count = 0
    try:
        if override_kwargs:
            override_count = Override.objects.filter(section=override_kwargs['master_section'].section).count()
    except AttributeError:
        pass
    if override_count == 0:
        topics = ScheduleTopic.objects.filter(unit__schedule=schedule)
        for topic in topics:
            if term.has_midpoint_break and topic.week >= ((term.length.num_weeks / 2) + 1):
                current_date = start_date + datetime.timedelta(days=(topic.week * 7))
            else:
                current_date = start_date + datetime.timedelta(days=((topic.week - 1) * 7))
            due_date = render_due_date(schedule, current_date, topic)
            pattern = '<td>' + due_date + '</td>'
            num_occurrences = len(re.findall(re.escape(pattern), html))
            html = sanitize_cell(html, pattern, num_occurrences)
    return html


def sanitize_cell(html, pattern, num_occurrences):
    """
    Sanitizes an individual cell (within a schedule).

    Parameters:
    :param (str) html:              A string containing the HTML to sanitize.
    :param (str) pattern:           The string to search for during sanitization.
    :param (int) num_occurrences:   The number of times that pattern appears within the HTML string.

    Returns:
    :return (string)                - Returns a string of sanitized HTML.
    """
    if num_occurrences > 1:
        pattern_corrected = pattern.replace('<td', '<td rowspan="' + str(num_occurrences) + '"')
        html = html.replace(pattern, pattern_corrected, 1)
        html = html.replace(pattern, '')
    return html

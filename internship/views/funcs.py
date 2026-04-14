from django.http import HttpResponseBadRequest, HttpResponse
import math
from django.shortcuts import get_object_or_404
from lti_tool.models import LtiLaunch

from core.views.funcs import handler403, handler404
from datetime import datetime
from internship.models import Internship, InternshipJournalEntry, InternshipSettings
from lti_tool.utils import get_launch_from_request
from lti_tool.models import LtiLaunch
from pylti1p3.grade import Grade
from viewer.models import SectionProgress


def calculate_grade(internship):
    """
    Calculates the grade for a given internship.

    Parameters:
    :param (Internship) internship:             The internship object for which to calculate a grade.

    Returns:
    return (None)                              - Returns None.
    """
    internship_settings = InternshipSettings.objects.get(coordinator=internship.section.instructor)
    max_points = internship_settings.journal_points
    total_points = (internship.completed_hours / internship_settings.journal_required_hours) * max_points
    if total_points > max_points:
        total_points = max_points
    return math.ceil(total_points), max_points


def update_completed_hours(request, internship_id):
    """
    Updates the completed hours field for an internship. Only verified entries are included.

    Parameters:
    :param (Request) request:                   The request object (for session variables).
    :param (int) internship_id:                 The id of the internship to update.

    Returns:
    return (None)                              - Returns None.
    """
    if request.user.is_authenticated:
        if request.user.has_perm('internship.update_internship'):
            internship = Internship.objects.get(pk=internship_id)
            entries = InternshipJournalEntry.objects.filter(location__internship=internship, verified=True)
            total_minutes = 0
            for entry in entries:
                total_minutes += entry.total_time_minutes
            internship.completed_hours = total_minutes / 60
            internship.save()
            return None
        else:
            return handler403(request)
    else:
        return handler404(request)


def update_grade(request, internship_id):
    """
    Sends an updated grade to the connected LTI system for an internship journal.

    Parameters:
    :param (Request) request:                   The request object (for session variables).
    :param (int) internship_id:                 The id of the internship to update.

    Returns:
    return (None)                              - Returns None.
    """
    if request.user.is_authenticated:
        if request.user.has_perm('internship.update_internship'):
            internship = Internship.objects.get(pk=internship_id)
            try:
                section_progress = SectionProgress.objects.get(section_id=internship.section_id, student=internship.intern)
                if section_progress.lti_launch_id:
                    total_points, max_points = calculate_grade(internship)
                    #lti_launch = get_launch_from_request(request, section_progress.lti_launch_id)

                    lti_launch = get_object_or_404(LtiLaunch, pk=section_progress.lti_launch_id)
                    launch = lti_launch.get_message_launch()
                    ags = launch.get_ags()

                    gr = Grade()
                    (gr.set_score_given(total_points)
                     .set_score_maximum(max_points)
                     .set_timestamp(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+0000'))
                     .set_activity_progress('Completed')
                     .set_grading_progress('FullyGraded')
                     .set_user_id(lti_launch.user.sub))
                    line_item = ags.find_lineitem('label', 'Internship Journal')
                    ags.put_grade(gr, line_item)
            except:
                pass
                #raise
                #raise TypeError('We were unable to send a grade back to Blackboard. Please contact your system '
                #                'administrator.')
        else:
            return handler403(request)
    else:
        return handler404(request)
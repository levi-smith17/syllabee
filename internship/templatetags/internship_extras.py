from django import template
from internship.views.funcs import calculate_grade
from internship.models import InternshipJournalEntry, Internship, InternshipSettings


register = template.Library()


@register.simple_tag()
def get_journal_entries(location_id):
    return InternshipJournalEntry.objects.filter(location_id=location_id)


@register.simple_tag
def get_total_internship_points(internship):
    total_points, max_points = calculate_grade(internship)
    return total_points, max_points


@register.simple_tag()
def get_total_time(internship_id, location_id, remaining):
    total_minutes = 0
    internship = Internship.objects.get(id=internship_id)
    internship_settings = InternshipSettings.objects.get(coordinator=internship.section.instructor)
    if remaining:
        total_minutes = (internship_settings.journal_required_hours * 60) - (internship.completed_hours * 60)
    else:
        if location_id:
            entries = InternshipJournalEntry.objects.filter(location_id=location_id, verified=True)
            for entry in entries:
                total_minutes += entry.total_time_minutes
        else:
            minutes = (internship.completed_hours * 60) % 60
            return int(internship.completed_hours), int(minutes)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return int(hours), int(minutes)

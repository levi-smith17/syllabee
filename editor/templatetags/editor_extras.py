from datetime import timedelta
from django import template
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from editor.models import Bond, CourseRequisite, MasterSyllabus, MasterBond, MasterBondSection, Segment, \
    MultipleChoiceQuestionResponse, ScheduleBlock
from editor.views.funcs import (is_addendum_necessary, is_segment_archived, is_segment_previously_published,
                                has_master_bonds, verify_block_course)
from viewer.models import SectionProgress

register = template.Library()


@register.simple_tag()
def get_average_completion_time(section):
    students = User.objects.filter(groups__name__in=['students'])
    section_progresses = SectionProgress.objects.filter(section=section, completed=True, student__in=students)
    total_students = section_progresses.count()
    if total_students > 0:
        total_time = timedelta(seconds=0)
        for section_progress in section_progresses:
            total_time += section_progress.stop_time - section_progress.start_time
        total_time = total_time / total_students
        hours, remainder = divmod(total_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        unit = ''
        if total_time.days > 0:
            unit += str(total_time.days) + ' day' + ('' if total_time.days == 1 else 's') + ', '
        if hours > 0:
            unit += str(hours) + ' hour' + ('' if hours == 1 else 's') + ', '
        if minutes > 0:
            unit += str(minutes) + ' minute' + ('' if minutes == 1 else 's') + ', '
        if seconds > 0:
            unit += str(seconds) + ' second' + ('' if seconds == 1 else 's')
        return mark_safe(unit)
    else:
        return 0

@register.simple_tag()
def get_master_bond(master_syllabus_id, segment_id):
    return MasterBond.objects.get(master_syllabus_id=master_syllabus_id, segment_id=segment_id)


@register.simple_tag()
def get_master_bond_sections(master_bond):
    return MasterBondSection.objects.filter(master_bond=master_bond).order_by('section__term')


@register.simple_tag()
def get_requisites_by_block(block):
    return CourseRequisite.objects.filter(requisite_block=block).order_by('order')


@register.simple_tag()
def get_responses(block_id):
    return (MultipleChoiceQuestionResponse.objects
            .filter(multiple_choice_question__id=block_id)
            .order_by('identifier'))


@register.simple_tag()
def get_total_students(mode, section):
    students = User.objects.filter(groups__name__in=['students'])
    if mode == 'completed':
        return SectionProgress.objects.filter(section=section, completed=True, student__in=students).count()
    elif mode == 'enrolled':
        return SectionProgress.objects.filter(section=section, student__in=students).count()
    else:
        return 0


@register.simple_tag(takes_context=True)
def filter_mbs(context, master_bond):
    return MasterBondSection.objects.filter(master_bond=master_bond, owner=context['request'].user)


@register.filter(name='has_at_least_one_master_bond')
def has_at_least_one_master_bond(master_syllabus_id):
    return has_master_bonds(master_syllabus_id)


@register.filter(name='is_dynamic_block')
def is_dynamic_block(block):
    if hasattr(block, 'printableblock'):
        if hasattr(block.printableblock, 'scheduleblock') or hasattr(block.printableblock, 'gradedeterminationblock'):
            return True
    return False


@register.filter(name='is_block_linked')
def is_block_linked(block):
    segments = Segment.objects.filter(bond__block_id=block.id)
    if segments:
        return True
    return False


@register.filter(name='is_offcanvas_expanded_editable')
def is_offcanvas_expanded_editable(block):
    if hasattr(block, 'printableblock'):
        if (hasattr(block.printableblock, 'contentblock') or hasattr(block.printableblock, 'detailsblock') or
                hasattr(block.printableblock, 'listblock') or hasattr(block.printableblock, 'scheduleblock') or
                hasattr(block.printableblock, 'tableblock')):
            return True
    elif hasattr(block, 'responseblock'):
        return True
    return False


@register.filter(name='is_printable_block')
def is_printable_block(block):
    return hasattr(block, 'printableblock')


@register.filter(name='is_segment_linked')
def is_segment_linked(segment):
    master_syllabi = MasterSyllabus.objects.filter(masterbond__segment_id=segment.id)
    if master_syllabi:
        return True
    return False


@register.simple_tag(takes_context=True)
def mb_get_first_section(context, master_bond):
    return MasterBondSection.objects.filter(master_bond=master_bond, section__isnull=False,
                                            owner=context['request'].user).first()


@register.simple_tag()
def replace_block_required(master_syllabus_id, segment_id, block_id):
    schedule_block = ScheduleBlock.objects.filter(id=block_id).exists()
    if schedule_block:
        return is_segment_archived(segment_id) or is_segment_previously_published(segment_id, master_syllabus_id)
    else:
        return (is_segment_archived(segment_id) or is_segment_previously_published(segment_id, master_syllabus_id) or
            is_addendum_necessary(master_syllabus_id, segment_id, block_id))


@register.simple_tag()
def response_letter(initial, increment):
    return chr(ord(initial) + increment)


@register.simple_tag(takes_context=True)
def segment_has_blocks(context, segment):
    return Bond.objects.filter(segment=segment, owner=context['request'].user).exists()


@register.filter(name='title')
def title(value):
    try:
        value = value.replace('_', ' ').title().split(' ')
        return ' '.join(list(dict.fromkeys(value)))
    except:
        return value


@register.simple_tag()
def verify_blk_course(master_syllabus, segment, block):
    return verify_block_course(master_syllabus, segment, block)


@register.simple_tag()
def verify_credit_hour_total(class_hours, lab_hours, total_hours):
    return total_hours == class_hours + lab_hours

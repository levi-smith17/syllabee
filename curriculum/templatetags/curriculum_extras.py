from django import template
from django.db.models import Q
from ..models import ProgramCourse, ProgramCourseExtension, ProgramTerm
from editor.models import CourseRequisite, CourseRequisiteBlock


register = template.Library()


@register.simple_tag()
def get_course_clock_hours(mode, course):
    hours = 0
    if mode == 'class':
        hours = (course.course.class_credit_hours * course.course.credit_hour_ratio.class_ratio)
    elif mode == 'lab':
        hours += (course.course.lab_credit_hours * course.course.credit_hour_ratio.lab_ratio)
    hours = float(f'{hours:.1f}')
    return hours


@register.simple_tag()
def get_course_extensions(course):
    return ProgramCourseExtension.objects.filter(related_course=course.course)


@register.simple_tag()
def get_footnotes(program):
    courses = (ProgramCourse.objects
               .filter(Q(term__program=program) & Q(footnote__isnull=False))
               .exclude(footnote='')
               .order_by('term__year__nominal', 'term__period__name', 'course__course_code'))
    footnotes = {}
    counter = 1
    for course in courses:
        if course.footnote not in footnotes.values():
            footnotes[counter] = course.footnote
            counter += 1
    return footnotes


@register.simple_tag()
def get_next_extension_operator(extensions, current_index):
    try:
        return extensions[int(current_index) + 1].operator
    except:
        return ''


@register.simple_tag()
def get_term_total(mode, program_id, term_id=None, credit_type=None):
    total = 0
    min_totals = []
    max_totals = []
    term = Q()
    credit_hour_type = Q()
    if term_id:
        term = Q(term__id=term_id)
    if credit_type:
        credit_hour_type = Q(credit_hour_type__id=credit_type)
    courses = (ProgramCourse.objects
               .filter(Q(term__program_id=program_id) & term & credit_hour_type)
               .exclude(pk__in=ProgramCourseExtension.objects.all()))
    for course in courses:
        extensions = ProgramCourseExtension.objects.filter(related_course=course.course)
        if extensions.exists():
            ext_total = []
            if mode == 'class':
                course_total = (course.course.class_credit_hours * course.course.credit_hour_ratio.class_ratio)
            elif mode == 'lab':
                course_total = (course.course.lab_credit_hours * course.course.credit_hour_ratio.lab_ratio)
            else:
                course_total = course.course.total_credit_hours
            for extension in extensions:
                if mode == 'class':
                    class_hours = extension.course.class_credit_hours * extension.course.credit_hour_ratio.class_ratio
                    if class_hours > 0:
                        ext_total.append(class_hours)
                elif mode == 'lab':
                    lab_hours = extension.course.lab_credit_hours * extension.course.credit_hour_ratio.lab_ratio
                    ext_total.append(lab_hours)
                else:
                    ext_total.append(extension.course.total_credit_hours)
            if course_total > 0:
                min_totals.append(min(course_total, *ext_total) + total)
                max_totals.append(max(course_total, *ext_total) + total)
            else:
                if len(ext_total) > 1:
                    min_totals.append(min(*ext_total) + total)
                    max_totals.append(max(*ext_total) + total)
                else:
                    min_totals.append(ext_total[0] + total)
                    max_totals.append(ext_total[0] + total)
        else:
            if mode == 'class':
                class_hours = (course.course.class_credit_hours * course.course.credit_hour_ratio.class_ratio)
                min_totals = [(x + class_hours) for x in min_totals]
                max_totals = [(x + class_hours) for x in max_totals]
                total += class_hours
            elif mode == 'lab':
                lab_hours = (course.course.lab_credit_hours * course.course.credit_hour_ratio.lab_ratio)
                min_totals = [(x + lab_hours) for x in min_totals]
                max_totals = [(x + lab_hours) for x in max_totals]
                total += lab_hours
            else:
                min_totals = [(x + course.course.total_credit_hours) for x in min_totals]
                max_totals = [(x + course.course.total_credit_hours) for x in max_totals]
                total += course.course.total_credit_hours
    if len(min_totals) > 0 and len(max_totals) > 0:
        minimum = int(min_totals[0]) if float(min_totals[0]).is_integer() else round(min_totals[0], 1)
        maximum = int(max_totals[0]) if float(max_totals[0]).is_integer() else round(max_totals[0], 1)
        if mode == 'class' or mode == 'lab':
            total = str(minimum) + '-' + str(maximum)
        else:
            total = str(maximum)
    else:
        total = int(total) if float(total).is_integer() else round(total, 1)
    return total


@register.simple_tag()
def verify_course(term, course):
    return verify_requisite(term, course) and verify_unique_courses(term, course)


@register.simple_tag()
def verify_requisite(term, course):
    q_program = Q(term__program=term.program)
    blocks = CourseRequisiteBlock.objects.filter(course=course).order_by('order')
    if blocks:
        block_result = False
        block_previous_result = False
        block_counter = 0
        for block in blocks:
            requisites = CourseRequisite.objects.filter(requisite_block=block).order_by('order')
            if requisites:
                requisite_result = False
                requisite_previous_result = False
                requisite_counter = 0
                for requisite in requisites:
                    q_prereq = (Q(course=requisite.requisite_course) &
                                (Q(term__year__nominal__lt=term.year.nominal) |
                                 (Q(term__year__nominal=term.year.nominal) &
                                  Q(term__period__name__lt=term.period.name))))
                    q_coreq = (Q(course=requisite.requisite_course) &
                               Q(term__year__nominal=term.year.nominal) &
                               Q(term__period__name=term.period.name))
                    if requisite.requisite_type:
                        if requisite_counter == 0:
                            requisite_result = ProgramCourse.objects.filter(q_program & q_prereq).exists()
                        else:
                            requisite_result = eval(str(ProgramCourse.objects.filter(q_program & q_prereq).exists()) +
                                                    ' ' + requisite.operator.lower() + ' ' +
                                                    str(requisite_previous_result))
                    else:
                        if requisite_counter == 0:
                            requisite_result = ProgramCourse.objects.filter(q_program & q_coreq).exists()
                        else:
                            requisite_result = eval(str(ProgramCourse.objects.filter(q_program & q_coreq).exists()) +
                                                    ' ' + requisite.operator.lower() + ' ' +
                                                    str(requisite_previous_result))
                    requisite_previous_result = requisite_result
                    requisite_counter += 1
            else:
                requisite_result = True
            if block_counter == 0:
                block_result = requisite_result
            else:
                block_result = eval(str(requisite_result) + ' ' + block.operator.lower() + ' ' +
                                    str(block_previous_result))
            block_previous_result = block_result
            block_counter += 1
        return block_result
    else:
        return True


@register.simple_tag()
def verify_term(term):
    return verify_unique_terms(term)


@register.simple_tag()
def verify_unique_terms(term):
    return ProgramTerm.objects.filter(program=term.program, year=term.year, period=term.period).count() <= 1


@register.simple_tag()
def verify_unique_courses(term, course):
    return ProgramCourse.objects.filter(term__program=term.program, course=course).count() <= 1

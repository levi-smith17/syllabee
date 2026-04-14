import datetime
from core.models import *
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q


DAYS_OF_THE_WEEK = (
    ('Sunday', 'Sunday'),
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
)
HEADINGS = (
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
)
LOGICAL_OPERATORS = (
    ('AND', 'AND'),
    ('OR', 'OR'),
)
MCQ_RESPONSES = (
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
)
REQUISITE_TYPES = (
    (True, 'Prerequisite'),
    (False, 'Co-Requisite'),
)
SECTION_FORMATS = (
    ('Lecture', 'Lecture'),
    ('Web-Flex', 'Web-Flex'),
    ('Independent Study', 'Independent Study'),
    ('Internship', 'Internship'),
    ('Online', 'Online'),
)
SEGMENT_HEADINGS = (
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
)
TABLE_ACCENTS = (
    ('', 'No Accent (Default)'),
    (' table-striped', 'Striped Rows'),
    (' table-dark table-hover', 'Hoverable Rows'),
)
TABLE_BORDERS = (
    ('', 'Row Borders Only (Default)'),
    (' table-bordered', 'Full Borders'),
    (' table-borderless', 'No Borders'),
)
TABLE_CELL_TYPE = (
    ('head', 'Header'),
    ('body', 'Body'),
    ('foot', 'Footer'),
)
TABLE_FOOTER_FUNCTION = (
    ('col_avg', 'Average of Column'),
    ('col_count', 'Count of Column'),
    ('col_min', 'Minimum of Column'),
    ('col_max', 'Maximum of Column'),
    ('col_sum', 'Sum of Column'),
    ('row_avg', 'Average of Row'),
    ('row_count', 'Count of Row'),
    ('row_min', 'Minimum of Row'),
    ('row_max', 'Maximum of Row'),
    ('row_sum', 'Sum of Row')
)
TARGETS = (
    ('_blank', 'Open in a new tab or window.'),
    ('_self', 'Open in same tab or window.'),
)


def create_path(instance, filename):
    return os.path.join(
        'profiles',
        instance.user.username,
        filename
    )


def create_block_path(instance, filename):
    return os.path.join(
        'blocks',
        str(instance.id),
        filename
    )


def create_section_path(instance, filename):
    return os.path.join(
        'sections',
        str(instance.id),
        filename
    )


class Branding(models.Model):
    institution = models.CharField(null=True, blank=True, max_length=100, help_text='Full name of institution.')
    core_values = models.TextField(null=True, blank=True, help_text='The institution\'s core values statement.')
    background_image = models.ImageField(null=True, blank=True, upload_to='admin/',
                                         help_text='An image used for the login page and main content background.')

    def filename(self):
        return os.path.basename(self.background_image.name)

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class ProfileManager(models.Manager):
    def search(self, pattern, user=None):
        q_objects = Q()
        q_objects.add(Q(user__last_name__icontains=pattern), Q.OR)
        q_objects.add(Q(user__first_name__icontains=pattern), Q.OR)
        q_objects.add(Q(user__email__icontains=pattern), Q.OR)
        q_objects.add(Q(preferred_name__icontains=pattern), Q.OR)
        q_objects.add(Q(secondary_email__icontains=pattern), Q.OR)
        q_objects.add(Q(office_location__icontains=pattern), Q.OR)
        q_objects.add(Q(office_phone__icontains=pattern), Q.OR)
        q_objects.add(Q(cell_phone__icontains=pattern), Q.OR)
        return super(ProfileManager, self).get_queryset().filter(q_objects)


class Profile(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    institution_id = models.IntegerField(default=0, help_text='A unique user ID assigned by your institution.')
    preferred_name = models.CharField(max_length=30, blank=True, null=True, help_text='The name you prefer to go by.')
    secondary_email = models.CharField(max_length=100, blank=True, null=True,
                                       help_text='An additional email address that can be used to contact you.')
    # Instructor-Only Profile Data
    title = models.CharField(max_length=100, null=True, blank=True, help_text='Your official title.')
    office_coordinates = models.CharField(max_length=100, null=True, blank=True,
                                          help_text='Geo coordinates representing the location of your office.')
    office_location = models.CharField(max_length=300, null=True, blank=True,
                                       help_text='The campus, building, and room number of where your office is '
                                                 'located.')
    office_phone = models.CharField(max_length=15, null=True, blank=True, help_text='Your office phone number.')
    cell_phone = models.CharField(max_length=15, null=True, blank=True, help_text='Your cell phone number.')
    # END Instructor-Only Profile Data
    website = models.CharField(max_length=500, null=True, blank=True, help_text='A URL pointing to your website.')
    facebook = models.CharField(max_length=500, null=True, blank=True, help_text='A URL pointing to your Facebook '
                                                                                 'profile.')
    twitter = models.CharField(max_length=500, null=True, blank=True, help_text='A URL pointing to your Twitter '
                                                                                'profile.')
    youtube = models.CharField(max_length=500, null=True, blank=True, help_text='A URL pointing to your YouTube '
                                                                                'channel.')
    picture = models.ImageField(null=True, blank=True, upload_to=create_path, help_text='Your profile picture.')

    objects = ProfileManager()

    class Meta:
        ordering = ('user__last_name', 'user__first_name',)

    def __str__(self):
        return str(self.user)

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class QuickLink(models.Model):
    name = models.CharField(max_length=60, help_text='The name of the quick link.')
    link = models.CharField(max_length=500, help_text='The hyperlink of the quick link.')
    target = models.CharField(max_length=20, choices=TARGETS, help_text='The action to be taken when this quick link '
                                                                        'is clicked.')
    restricted = models.BooleanField(default=False, help_text='Whether this quick link is restricted or not. A '
                                                              'restricted quick link can only be viewed by instructors '
                                                              'or admins.')

    class Meta:
        ordering = ('name',)
        verbose_name = 'quick link'

    def __str__(self):
        return self.name

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class CourseRatioManager(models.Manager):
    def search(self, pattern, user=None):
        q_objects = Q()
        q_objects.add(Q(name__icontains=pattern), Q.OR)
        q_objects.add(Q(class_ratio__icontains=pattern), Q.OR)
        q_objects.add(Q(lab_ratio__icontains=pattern), Q.OR)
        return super(CourseRatioManager, self).get_queryset().filter(q_objects)


class CourseRatio(models.Model):
    name = models.CharField(max_length=60, help_text='The name of the course ratio.')
    class_ratio = models.FloatField(help_text='The class ratio.')
    lab_ratio = models.FloatField(help_text='The lab ratio.')

    objects = CourseRatioManager()

    class Meta:
        ordering = ('name',)
        verbose_name = 'course ratio'
        verbose_name_plural = 'course ratios'

    def __str__(self):
        return self.name

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class CourseManager(models.Manager):
    def search(self, pattern, user=None):
        q_objects = Q()
        q_objects.add(Q(prefix__icontains=pattern), Q.OR)
        q_objects.add(Q(number__icontains=pattern), Q.OR)
        q_objects.add(Q(course_code__icontains=pattern), Q.OR)
        q_objects.add(Q(name__icontains=pattern), Q.OR)
        q_objects.add(Q(credit_hour__icontains=pattern), Q.OR)
        if not user.groups.filter('admins') and user.groups.filter('instructors'):
            q_objects.add(Q(owner=user), Q.AND)
        return super(CourseManager, self).get_queryset().filter(q_objects)


class Course(models.Model):
    prefix = models.CharField(max_length=3, help_text='The prefix associated with this course (e.g. CIS).')
    number = models.CharField(max_length=4, help_text='The number associated with this course (e.g. 211S).')
    course_code = models.CharField(max_length=8)
    name = models.CharField(max_length=60, help_text='The name of this course (e.g. Operating System Concepts).')
    total_credit_hours = models.FloatField(help_text='The number of credit hours associated with this course (e.g. '
                                                     '3.0).')
    class_credit_hours = models.FloatField(help_text='The number of class credit hours for this course. Class credit '
                                                     'hours and lab credit hours must add up to total credit hours.')
    lab_credit_hours = models.FloatField(help_text='The number of lab credit hours for this course. Class credit hours '
                                                   'and lab credit hours must add up to total credit hours.')
    credit_hour_ratio = models.ForeignKey(CourseRatio, on_delete=models.CASCADE,
                                    help_text='Determines how credit hours are converted to clock hours.')
    inactive = models.BooleanField(default=False, help_text='Whether this course is inactive or not. If a course is '
                                                            'made inactive, it will be hidden from all course input '
                                                            'boxes throughout the app.')
    future_name = models.CharField(max_length=60, blank=True, null=True,
                                   help_text='A future name for this course (for use in the Curriculum Builder tool).')
    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    objects = CourseManager()

    class Meta:
        ordering = ('prefix', 'number', 'name',)
        verbose_name = 'course'
        verbose_name_plural = 'courses'

    def to_str_section(self):
        return str(self.course_code)

    def __str__(self):
        return (((self.prefix + '-' + self.number + ' - ') if self.prefix != 'ZZZ' else '') + self.name +
                (' (INACTIVE)' if self.inactive else ''))

    @classmethod
    def delete_warning(cls):
        return 'Note: a course cannot be deleted if sections are associated with it.'

    @classmethod
    def filterable(cls):
        return True

    @classmethod
    def get_exclusions(cls, user):
        if user.groups.filter(name='admins'):
            return None
        if user.groups.filter(name='instructors'):
            return Q(owner=user)


class CourseRequisiteBlock(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    operator = models.CharField(max_length=3, choices=LOGICAL_OPERATORS,
                                help_text='The logical operator used between this requisite block and the previous '
                                          'requisite block.')
    order = models.PositiveIntegerField(default=10, help_text='The order of this requisite block.')

    class Meta:
        ordering = ('order',)
        verbose_name = 'course requisite block'
        verbose_name_plural = 'course requisite blocks'

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class CourseRequisite(models.Model):
    requisite_course = models.ForeignKey(Course, on_delete=models.CASCADE, help_text='The course for this requisite.')
    requisite_type = models.BooleanField(default=True, choices=REQUISITE_TYPES, help_text='The type of this requisite.')
    operator = models.CharField(max_length=3, choices=LOGICAL_OPERATORS,
                                help_text='The logical operator used between this requisite and and previous '
                                          'requisites within this block.')
    order = models.PositiveIntegerField(default=10, help_text='The order of this requisite block.')
    requisite_block = models.ForeignKey(CourseRequisiteBlock, on_delete=models.CASCADE)

    class Meta:
        ordering = ('order',)
        verbose_name = 'course requisite'
        verbose_name_plural = 'course requisites'

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class TermLengthManager(models.Manager):
    def search(self, pattern, user=None):
        q_objects = Q()
        q_objects.add(Q(name__icontains=pattern), Q.OR)
        q_objects.add(Q(num_weeks__icontains=pattern), Q.OR)
        return super(TermLengthManager, self).get_queryset().filter(q_objects)


class TermLength(models.Model):
    name = models.CharField(max_length=50, help_text='The name of this term length.')
    num_weeks = models.IntegerField(help_text='The number of weeks within this term length.')
    can_have_midpoint_break = models.BooleanField(default=False, choices=BOOLEAN_CHOICES,
                                                  help_text='Whether this term length can have a midpoint break or '
                                                            'not (e.g., spring break). Note: setting this field '
                                                            'incorrectly could cause errors for users. It should only '
                                                            'be applied to terms that are divided around a midpoint '
                                                            'break.')

    objects = TermLengthManager()

    class Meta:
        ordering = ('num_weeks',)
        verbose_name = 'term length'
        verbose_name_plural = 'term lengths'

    def __str__(self):
        return str(self.num_weeks) + ' Week' + ('s' if self.num_weeks != 0 else '')

    @classmethod
    def delete_warning(cls):
        return 'Note: a term length cannot be deleted if terms are associated with it.'

    @classmethod
    def filterable(cls):
        return False


class TermManager(models.Manager):
    def search(self, pattern, user=None):
        q_objects = Q()
        q_objects.add(Q(term_code__icontains=pattern), Q.OR)
        q_objects.add(Q(name__icontains=pattern), Q.OR)
        q_objects.add(Q(length__name__icontains=pattern), Q.OR)
        q_objects.add(Q(length__num_weeks__icontains=pattern), Q.OR)
        q_objects.add(Q(start_date__icontains=pattern), Q.OR)
        q_objects.add(Q(end_date__icontains=pattern), Q.OR)
        return super(TermManager, self).get_queryset().filter(q_objects)


class Term(models.Model):
    term_code = models.CharField(max_length=6, unique=True, help_text='The code associated with this term (e.g. '
                                                                      '2022FS).')
    name = models.CharField(max_length=30, help_text='The full name of this term (e.g. Fall 2022)')
    length = models.ForeignKey(TermLength, on_delete=models.PROTECT, help_text='The number of weeks in this term.')
    start_date = models.DateField(help_text='The start date of this term. Should be a Monday.')
    end_date = models.DateField(help_text='The end date of this term. Should be a Saturday.')
    has_midpoint_break = models.BooleanField(default=False, help_text='Whether this term has a midpoint break (e.g. '
                                                                      'spring break) or not.')
    supports_master_syllabi = models.BooleanField(default=False, help_text='Whether this term can be used to create '
                                                                           'a corresponding master syllabus or not. '
                                                                           'This option should only be set to Yes on '
                                                                           'the longest term lengths possible.')
    archived = models.BooleanField(default=False)

    objects = TermManager()

    class Meta:
        ordering = ('-term_code',)
        verbose_name = 'term'
        verbose_name_plural = 'terms'

    def __str__(self):
        return self.term_code + (' (ARCHIVED)' if self.archived else '')

    @classmethod
    def delete_warning(cls):
        return 'Note: a term cannot be deleted if sections are assigned to it.'

    @classmethod
    def filterable(cls):
        return False


class SectionManager(models.Manager):
    def search(self, pattern, user=None):
        q_objects = Q()
        q_objects.add(Q(term__term_code__icontains=pattern), Q.OR)
        q_objects.add(Q(section_code__icontains=pattern), Q.OR)
        q_objects.add(Q(course__prefix__icontains=pattern), Q.OR)
        q_objects.add(Q(course__number__icontains=pattern), Q.OR)
        q_objects.add(Q(course__course_code__icontains=pattern), Q.OR)
        q_objects.add(Q(course__name__icontains=pattern), Q.OR)
        q_objects.add(Q(instructor__last_name__icontains=pattern), Q.OR)
        q_objects.add(Q(instructor__first_name__icontains=pattern), Q.OR)
        if not user.groups.filter(name='admins') and user.groups.filter(name='instructors'):
            q_objects.add(Q(owner=user), Q.AND)
        return super(SectionManager, self).get_queryset().filter(q_objects)


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT,
                               help_text='The course associated with this section (e.g. CIS-211S). Can be selected '
                                         'from the drop-down list or typed into the input box, but must match a valid '
                                         'course.')
    section_code = models.CharField(max_length=5, help_text='The unique code assigned to this section (e.g. 401FS).')
    term = models.ForeignKey(Term, on_delete=models.PROTECT,
                             help_text='The term associated with this section (e.g. 2022FS). Can be selected from the '
                                       'drop-down list or typed into the input box, but must match a valid term.')
    instructor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='instructor',
                                   help_text='The instructor assigned to teach this section. Can be selected from the '
                                             'drop-down list or typed into the input box, but must match a valid '
                                             'instructor\'s name.')
    format = models.CharField(max_length=20, choices=SECTION_FORMATS, help_text='The format of this course section (should '
                                                                                'coincide with the Section Code).')
    archived_syllabus = models.FileField(upload_to=create_section_path, null=True, blank=True, default=None,
                                         help_text='An archived syllabus associated with this course section for '
                                                   'historical purposes. This option should only be used for syllabi '
                                                   'that were not created within this app.')
    hash = models.CharField(max_length=40, help_text='The auto-generated hash value for this section.')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='owner')

    objects = SectionManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'section_code', 'term'], name='unique_registration_section_constraint'
            )
        ]
        ordering = ('-term__term_code', 'course__prefix', 'course__number', 'section_code',)
        verbose_name = 'section'
        verbose_name_plural = 'sections'

    def __str__(self):
        return self.course.to_str_section() + '-' + self.section_code + '-' + self.term.term_code + \
            (' (ARCHIVED)' if self.term.archived or self.archived_syllabus else '')

    @classmethod
    def delete_warning(cls):
        return 'Note: a section cannot be deleted if students are enrolled in it.'

    @classmethod
    def filterable(cls):
        return True

    @classmethod
    def get_exclusions(cls, user):
        if user.groups.filter(name='admins'):
            return None
        if user.groups.filter(name='instructors'):
            return Q(owner=user)


class GradingScale(models.Model):
    name = models.CharField(max_length=30, help_text='The name of this grading scale.')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('owner', 'name',)
        verbose_name = 'grading scale'
        verbose_name_plural = 'grading scales'

    def __str__(self):
        return self.name

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class GradingScaleGrade(models.Model):
    letter = models.CharField(max_length=2, help_text='The letter grade associated with this row (e.g. A).')
    percent_start = models.FloatField(help_text='The start of this range as a percentage (e.g. 89.5). No need to add '
                                                'a percent sign.')
    percent_end = models.FloatField(help_text='The end of this range as a percentage (e.g. 100). No need to add a '
                                              'percent sign.')
    grading_scale = models.ForeignKey(GradingScale, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['grading_scale', 'letter'], name='unique_editor_grade_letter_constraint'
            )
        ]
        ordering = ('grading_scale', 'letter',)

    def __str__(self):
        return self.letter


class Message(models.Model):
    name = models.CharField(max_length=30, help_text='An internal name for this message.')
    description = models.CharField(max_length=300, help_text='An internal description for this message.')
    subject = models.CharField(max_length=100, help_text='The subject of the email message to be sent.')
    body = models.TextField(help_text='The body of the email message to be sent. Supports HTML.')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('owner', 'name',)
        verbose_name = 'message'
        verbose_name_plural = 'messages'

    def __str__(self):
        return self.name

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class ScheduleManager(models.Manager):
    def search(self, pattern, user=None):
        q_objects = Q()
        q_objects.add(Q(course__inactive=False), Q.AND)
        q_objects.add(Q(owner=user), Q.AND)
        q_objects.add(Q(course__prefix__icontains=pattern), Q.OR)
        q_objects.add(Q(course__number__icontains=pattern), Q.OR)
        q_objects.add(Q(course__course_code__icontains=pattern), Q.OR)
        q_objects.add(Q(term_length__name__icontains=pattern), Q.OR)
        q_objects.add(Q(term_length__num_weeks__icontains=pattern), Q.OR)
        q_objects.add(Q(description__icontains=pattern), Q.OR)
        return super(ScheduleManager, self).get_queryset().filter(q_objects)


class Schedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               help_text='The course that this schedule is associated with. Can be selected from the '
                                         'drop-down list or typed into the input box, but must match a valid course.')
    term_length = models.ForeignKey(TermLength, on_delete=models.PROTECT,
                                    help_text='The number of weeks within this schedule. Note: terms with a midpoint '
                                              'break (i.e. spring break) are handled automatically.')
    description = models.TextField(max_length=1000, blank=True, help_text='A description for this schedule, which is '
                                                                          'displayed to students immediately above it.')
    display_units_column = models.BooleanField(default=True, help_text='Whether the Units column is displayed on a '
                                                                       'schedule or not.')
    assignment_due_day = models.CharField(max_length=10, default='Monday', choices=DAYS_OF_THE_WEEK,
                                          help_text='The day of the week that your assignments are generally due. Due '
                                                    'dates can be individually overridden once this schedule is added '
                                                    'to a segment (from the block editor).')
    assignment_due_time = models.TimeField(default=datetime.time(23, 59, 0),
                                           help_text='The time of day that your assignments are generally due. Can '
                                                     'be individually overridden.')
    finals_due_day = models.CharField(max_length=10, default='Monday', choices=DAYS_OF_THE_WEEK,
                                      help_text='The day of finals week that your assignments are due. Can be '
                                                'individually overridden.')
    finals_due_time = models.TimeField(default=datetime.time(23, 59, 0),
                                       help_text='The time of day that your final assignments are due. Can be '
                                                 'individually overridden.')
    effective_term = models.ForeignKey(Term, null=True, blank=True, on_delete=models.SET_NULL,
                                       help_text='The first term that this schedule is effective.')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = ScheduleManager()

    class Meta:
        ordering = ('owner', 'course', 'term_length',)
        verbose_name = 'schedule'
        verbose_name_plural = 'schedules'

    def __str__(self):
        return str(self.course) + ' - ' + str(self.term_length) + \
            (' - (W.e.f. ' + str(self.effective_term) + ')' if self.effective_term else '')

    @classmethod
    def delete_warning(cls):
        return 'Note: any associated units, topics, and assignments will also be deleted.'

    @classmethod
    def filterable(cls):
        return True


class ScheduleUnit(models.Model):
    week = models.PositiveIntegerField(help_text='The week number that this unit starts in.')
    number = models.PositiveIntegerField(help_text='A number assigned to this unit within this course. Should be used '
                                                   'to sequence units.')
    name = models.CharField(max_length=200, help_text='The name of this unit.')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('owner', 'schedule', 'number',)

    def __str__(self):
        return 'Unit ' + str(self.number).rjust(2, '0') + ' - ' + self.name

    @classmethod
    def delete_warning(cls):
        return 'Note: any associated topics and assignments will also be deleted.'

    @classmethod
    def filterable(cls):
        return False


class ScheduleTopic(models.Model):
    week = models.PositiveIntegerField(help_text='The week number that this topic starts in.')
    unit = models.ForeignKey(ScheduleUnit, on_delete=models.CASCADE, help_text='The unit that this topic belongs to.')
    number = models.PositiveIntegerField(null=True, blank=True,
                                         help_text='A number assigned to this topic within this course. Should be '
                                                   'used to sequence topics, but can be left blank to add general '
                                                   'notes to the Topic column.')
    name = models.CharField(max_length=200, help_text='The name of this topic.')
    emphasize_topic = models.BooleanField(default=False, help_text='Formats this topic\'s name in bold.')
    reading = models.CharField(max_length=200, null=True, blank=True,
                               help_text='The assigned reading assignments for this topic. If left blank, \'N/A\' '
                                         'will be displayed.')
    assignment_name = models.CharField(max_length=200, null=True, blank=True,
                                       help_text='The name of the assignment for this topic. If left blank, \'N/A\' '
                                                 'will be displayed.')
    emphasize_assignment = models.BooleanField(default=False, help_text='Formats this assignment\'s name in bold.')
    assignment_category = models.CharField(max_length=100, null=True, blank=True,
                                           help_text='Associating assignments with a category allows the grade '
                                                     'determination block to provide a list of categories and their '
                                                     'respective point values (assuming point values are supplied as '
                                                     'well).')
    assignment_points = models.IntegerField(default=0, help_text='The number of points that this assignment is worth. '
                                                                 'If set to zero, \'N/A\' will be displayed. Can be '
                                                                 'used with categories as described above.')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('owner', 'unit', 'week', 'emphasize_topic', 'number',)

    def __str__(self):
        if self.number:
            return 'Topic ' + str(self.number).rjust(2, '0') + ' - ' + self.name
        else:
            return self.name

    @classmethod
    def delete_warning(cls):
        return 'Note: any associated assignments will also be deleted.'

    @classmethod
    def filterable(cls):
        return False


class MasterSyllabusManager(models.Manager):
    def search(self, pattern, user=None):
        q_objects = Q()
        q_objects.add(Q(term__term_code__icontains=pattern), Q.OR)
        q_objects.add(Q(term__name__icontains=pattern), Q.OR)
        q_objects.add(Q(term__length__name__icontains=pattern), Q.OR)
        q_objects.add(Q(term__length__num_weeks__icontains=pattern), Q.OR)
        q_objects.add(Q(term__start_date__icontains=pattern), Q.OR)
        q_objects.add(Q(term__end_date__icontains=pattern), Q.OR)
        q_objects.add(Q(owner=user), Q.AND)
        return super(MasterSyllabusManager, self).get_queryset().filter(q_objects)


class MasterSyllabus(models.Model):
    term = models.ForeignKey(Term, on_delete=models.PROTECT,
                             help_text='The term that this master syllabus is assigned to. Master syllabi can only be '
                                       'assigned to a single term. A single master syllabus can be used for multiple '
                                       'terms with the same start date automatically. In this case, the master '
                                       'syllabus should be assigned to the longest term. This setting cannot be '
                                       'changed once saved.')
    office_hours = models.TextField(null=True, blank=True, help_text='Your scheduled office hours for the term.')
    interactive_view = models.BooleanField(default=True,
                                           help_text='The view students use to access a syllabus. The interactive '
                                                     'view requires a student to navigate content block-by-block. '
                                                     'Students are not able to view the entire syllabus until '
                                                     'they\'ve completely navigated the entire interactive syllabus. '
                                                     'The traditional view allows a student to access an entire '
                                                     'syllabus at once at all times. A traditional syllabus is '
                                                     'also accessible to any unauthenticated user with the syllabus\'s '
                                                     'URL.')
    timeout = models.IntegerField(default=3000, help_text='The amount of time in milliseconds that a student must '
                                                          'wait before they are able to click the Next button within '
                                                          'an interactive syllabus. Has no effect within a traditional '
                                                          'view.')
    prohibit_backtracking = models.BooleanField(default=False, help_text='Prohibits students from accessing previously '
                                                                         'completed blocks while on a response block. '
                                                                         'Note: enabling this feature also prohibits '
                                                                         'students from using the Table of Contents '
                                                                         'to navigate between blocks.')
    max_attempts = models.IntegerField(default=0, help_text='The maximum number of attempts a student has within a '
                                                            'response block. A value of 0 indicates that students will '
                                                            'have unlimited attempts within each response block. Can '
                                                            'be overridden per response block.')
    max_points = models.IntegerField(default=0, help_text='The maximum number of points a student has within a '
                                                          'response block. Can be overridden per response block.')
    randomize_responses = models.BooleanField(default=True, help_text='Randomizes the responses within each response '
                                                                      'block for each attempt.')
    points_ladder = models.BooleanField(default=False, help_text='Using this option causes a point to be deducted for '
                                                                 'each incorrect response within a response block. '
                                                                 'This setting requires that the maximum number of '
                                                                 'attempts be less than the number of responses within '
                                                                 'a response block. Otherwise, this setting has no '
                                                                 'effect.')
    points_ladder_deduction = models.IntegerField(default=1, help_text='The number of points to be deducted for each '
                                                                       'incorrect response withing a response block. '
                                                                       'This setting has no effect if the previous '
                                                                       'setting is set to No.')
    locked = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    objects = MasterSyllabusManager()

    class Meta:
        ordering = ('owner', 'term',)
        verbose_name = 'master syllabus'
        verbose_name_plural = 'master syllabi'

    def __str__(self):
        return 'Master Syllabus - ' + self.term.name + (' (ARCHIVED)' if self.term.archived else '')

    @classmethod
    def delete_warning(cls):
        return 'Note: any associated segments will be unlinked and can be relinked using the <strong>Copy ' \
               'Content</strong> option.'

    @classmethod
    def filterable(cls):
        return False


class Segment(models.Model):
    name = models.CharField(max_length=100, help_text='The name of this segment.')
    description = models.TextField(help_text='The description of this segment (visible to students).')
    print_heading = models.CharField(max_length=1, default=2, choices=SEGMENT_HEADINGS,
                                     help_text='The heading level of this segment. Used to properly format segments '
                                               'for printing. For example, a segment that should be indented under '
                                               'another segment should have a heading of 4 (while it\'s preceding '
                                               'segment should have a heading of 3).')
    printing_optional = models.BooleanField(default=False,
                                            help_text='Prevents the content of this segment from being printed '
                                                      'automatically when students go to print a traditional syllabus. '
                                                      'Instead, students are presented with an option to manually '
                                                      'select this content for printing.')
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    effective_term = models.ForeignKey(Term, null=True, blank=True, on_delete=models.SET_NULL,
                                       help_text='The term that this segment is effective. Assists in identifying '
                                                 'segments in various pick lists.')

    class Meta:
        ordering = ('owner',)
        verbose_name = 'segment'

    def __str__(self):
        return self.name

    @classmethod
    def delete_warning(cls):
        return 'Note: any associated blocks will be unlinked and available using the Copy Content option.'

    @classmethod
    def filterable(cls):
        return False


class MasterBond(models.Model):
    master_syllabus = models.ForeignKey(MasterSyllabus, on_delete=models.CASCADE)
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE,
                                help_text='The segment that will be assigned to this master syllabus. Must be a valid '
                                          'segment from the list below. Duplicate segments cannot be added.')
    # The order of the segments within each master segment.
    visibility = models.BooleanField(default=False, help_text='Whether or not this segment is visible to students.')
    order = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['master_syllabus', 'segment'], name='unique_editor_master_bond_constraint'
            )
        ]
        ordering = ('owner', 'order',)

    def __str__(self):
        return str(self.master_syllabus) + ' | ' + str(self.segment)

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class MasterBondSectionManager(models.Manager):
    def search(self, pattern, user=None):
        q_objects = Q()
        q_objects.add(Q(section__term__term_code__icontains=pattern), Q.OR)
        q_objects.add(Q(section__section_code__icontains=pattern), Q.OR)
        q_objects.add(Q(section__course__prefix__icontains=pattern), Q.OR)
        q_objects.add(Q(section__course__number__icontains=pattern), Q.OR)
        q_objects.add(Q(section__course__course_code__icontains=pattern), Q.OR)
        q_objects.add(Q(section__course__name__icontains=pattern), Q.OR)
        q_objects.add(Q(section__instructor__last_name__icontains=pattern), Q.OR)
        q_objects.add(Q(section__instructor__first_name__icontains=pattern), Q.OR)
        return super(MasterBondSectionManager, self).get_queryset().filter(q_objects)


class MasterBondSection(models.Model):
    master_bond = models.ForeignKey(MasterBond, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.PROTECT)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    objects = MasterBondSectionManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['master_bond', 'section'], name='unique_editor_master_bond_section_constraint'
            )
        ]
        ordering = ('owner', 'section',)
        verbose_name = 'section'
        verbose_name_plural = 'sections'

    def __str__(self):
        return str(self.master_bond) + ' | ' + str(self.section)

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return True


class Block(models.Model):
    name = models.CharField(max_length=100, help_text='The name of this block.')
    type = models.CharField(max_length=30)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        ordering = ('owner', 'bond__order')

    def __str__(self):
        return self.name + ' (' + self.type.replace('_', ' ').title() + ')'

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class PrintableBlock(Block):
    print_heading = models.CharField(max_length=1, default=3, choices=HEADINGS,
                                     help_text='The heading level of this block. Used to properly format blocks for '
                                               'printing. For example, a block that should be indented under another '
                                               'block should have a heading of 4 (while it\'s preceding block should '
                                               'have a heading of 3).')
    print_group = models.CharField(max_length=30, null=True, blank=True,
                                   help_text='The print group that this block is assigned to. Print groups are '
                                             'used to merge content together during printing (it combines separate '
                                             'blocks into a single block during printing).')
    published = models.BooleanField(default=False, help_text='Publishing this block makes it directly accessible via a '
                                                             'URL (without the need for accessing it via a syllabus).')
    permalink = models.CharField(max_length=200, blank=True, null=True)
    effective_term = models.ForeignKey(Term, null=True, blank=True, on_delete=models.SET_NULL,
                                       help_text='The first term that this block is effective.')


class ContentBlock(PrintableBlock):
    content = models.TextField(max_length=1500, null=True, blank=True,
                               help_text='The content of this block. Must be less than 1500 characters.')
    image = models.ImageField(null=True, blank=True, upload_to=create_block_path,
                              help_text='An optional image that accompanies this content.')
    image_position = models.CharField(max_length=20, null=True, blank=True, choices=(
        ('Before Content', 'Before Content'),
        ('After Content', 'After Content')), help_text='Whether to position this image before the content (above) or '
                                                       'after it.')

    class Meta:
        verbose_name = 'content block'


class DetailsBlock(PrintableBlock):
    class Meta:
        verbose_name = 'details block'


class DetailsBlockDetail(models.Model):
    summary = models.CharField(max_length=500, help_text='The text that can be expanded to view details.')
    content = models.TextField(help_text='The text that is displayed when the summary is clicked.')
    order = models.IntegerField(help_text='A number used to sequence all details (it\'s recommended to use '
                                          'multiples of ten).')
    details_block = models.ForeignKey(DetailsBlock, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('owner', 'order',)
        verbose_name = 'detail'

    def __str__(self):
        return self.summary

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class FileBlock(PrintableBlock):
    file = models.FileField(upload_to=create_block_path, help_text='The file associated with this block.')
    description = models.TextField(max_length=500, blank=True, null=True,
                                   help_text='A description to accompany this file.')

    class Meta:
        verbose_name = 'file block'


class CourseSyllabusBlock(FileBlock):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, help_text='The course associated with this syllabus.')

    class Meta:
        verbose_name = 'course syllabus block'


class GradeDeterminationBlock(PrintableBlock):
    grading_scale = models.ForeignKey(GradingScale, on_delete=models.PROTECT,
                                      help_text='The grading scale used for this grade determination block. Additional '
                                                'grading scales can be added from the Grading Scales menu on the right-'
                                                'hand sidebar.')
    description = models.TextField(max_length=1000, blank=True,
                                   help_text='A description to accompany this grade determination block, which is '
                                             'displayed to students immediately above it.')
    schedule = models.ForeignKey('ScheduleBlock', null=True, blank=True, on_delete=models.SET_NULL,
                                 help_text='If a schedule is supplied with assignment categories established, then '
                                           'it will be used to generate a breakdown of those points by category.')

    class Meta:
        verbose_name = 'grade determination block'


class ListBlock(PrintableBlock):
    list_type = models.CharField(max_length=10, choices=(('Ordered', 'Ordered'), ('Unordered', 'Unordered')),
                                 help_text='Whether this list should be ordered (using one of the options in the '
                                           'ordered type field below) or unordered (bulleted).')
    ordered_start = models.IntegerField(blank=True, null=True,
                                        help_text='The starting value of this ordered list. Only applies to Ordered '
                                                  'list blocks.')
    ordered_type = models.CharField(blank=True, null=True, max_length=1,
                                    choices=(('1', '1'), ('A', 'A'), ('a', 'a'), ('I', 'I'), ('i', 'i')),
                                    help_text='The type of marker to use within this list. Only applies to Ordered '
                                              'list blocks')

    class Meta:
        verbose_name = 'list block'


class ListBlockItem(models.Model):
    content = models.TextField(max_length=500, help_text='The content of this list item (supports HTML).')
    order = models.IntegerField(help_text='A number used to sequence all list items (it\'s recommended to use '
                                          'multiples of ten).')
    parent_item = models.ForeignKey('ListBlockItem', blank=True, null=True, on_delete=models.CASCADE,
                                    help_text='This option can be used to nest this list item beneath another.')
    list_block = models.ForeignKey(ListBlock, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('owner', 'order',)
        verbose_name = 'list block item'

    def __str__(self):
        return self.content

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class ScheduleBlock(PrintableBlock):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE,
                                 help_text='The schedule assigned to this block. Must match the course associated '
                                           'with this segment.')

    class Meta:
        verbose_name = 'schedule block'


class TableBlock(PrintableBlock):
    number_of_columns = models.IntegerField(default=3, blank=True, help_text='The number of columns within this table.')
    caption = models.CharField(max_length=200, null=True, blank=True,
                               help_text='The caption associated with this table.')
    caption_position = models.CharField(max_length=10, null=True, blank=True,
                                        choices=(('bottom', 'Bottom'), ('top', 'Top')),
                                        help_text='The location of the caption for this table.')
    accent = models.CharField(max_length=30, blank=True, choices=TABLE_ACCENTS,
                              help_text='The accent style for this table.')
    borders = models.CharField(max_length=30, blank=True, choices=TABLE_BORDERS,
                               help_text='The border style for this table.')
    has_group_dividers = models.BooleanField(default=False, null=True, blank=True,
                                             help_text='Adds a thicker border between the table\'s header, body, and '
                                                       'footer sections.')

    class Meta:
        verbose_name = 'table block'
        verbose_name_plural = 'table blocks'

    @classmethod
    def delete_warning(cls):
        return 'Note: any associated column(s), row(s), or cell(s) will also be deleted.'

    @classmethod
    def filterable(cls):
        return False


class TableBlockColumn(models.Model):
    table = models.ForeignKey(TableBlock, on_delete=models.CASCADE, help_text='The table that this column belongs to.')
    column_number = models.IntegerField(help_text='The column number of this column within the table.')
    span = models.IntegerField(default=1, blank=True, help_text='A numeric value representing how many columns this '
                                                                'column group should span.')
    style = models.CharField(max_length=2000, blank=True,
                             help_text='CSS styles for this column group provided as a CSS string for an inline HTML '
                                       'style attribute.')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'table block column'
        verbose_name_plural = 'table block columns'

    @classmethod
    def delete_warning(cls):
        return 'Note: any associated table cell(s) will also be deleted.'

    @classmethod
    def filterable(cls):
        return False


class TableBlockRow(models.Model):
    table = models.ForeignKey(TableBlock, on_delete=models.CASCADE, help_text='The table that this row belongs to.')
    type = models.CharField(max_length=4, choices=TABLE_CELL_TYPE, default='body', help_text='The section this row '
                                                                                             'belongs to.')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'table block row'
        verbose_name_plural = 'table block rows'

    @classmethod
    def delete_warning(cls):
        return 'Note: any associated table cell(s) will also be deleted.'

    @classmethod
    def filterable(cls):
        return False


class TableBlockCell(models.Model):
    table_row = models.ForeignKey(TableBlockRow, on_delete=models.CASCADE, help_text='The table row that this cell '
                                                                                     'belongs to.')
    column_number = models.IntegerField(help_text='The column number of this cell.')
    value = models.CharField(max_length=2000, blank=True, help_text='The value for this cell.')
    colspan = models.IntegerField(default=1, help_text='A numeric value representing how many columns this cell '
                                                       'should span.')
    rowspan = models.IntegerField(default=1, help_text='A numeric value representing how many rows this cell should '
                                                       'span.')
    aggregate_function = models.CharField(max_length=10, null=True, blank=True, choices=TABLE_FOOTER_FUNCTION,
                                          help_text='The function used on this cell\'s column or row. Must be in a '
                                                    'row footer or the last column of a row. Displays instead '
                                                    'of the cell value (provided above).')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'table block cell'
        verbose_name_plural = 'table block cells'

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class VideoBlock(PrintableBlock):
    embed_code = models.TextField(help_text='The embed code from the site hosting the video. Should be in HTML format.')
    content_verbose = models.TextField(null=True, blank=True,
                                       help_text='Text-based content that is used in place of video content on a '
                                                 'traditional syllabus.')

    class Meta:
        verbose_name = 'video block'


class ResponseBlock(Block):
    max_attempts = models.PositiveIntegerField(default=0, help_text='The maximum number of attempts a student has at '
                                                                    'this question. If a value other than 0 is '
                                                                    'provided, then this value overrides the value set '
                                                                    'on the master syllabus.')
    max_points = models.PositiveIntegerField(default=0, help_text='The maximum number of points that can be earned for '
                                                                  'this question. If a value other than 0 is provided, '
                                                                  'then this value overrides the value set on the '
                                                                  'master syllabus.')
    class Meta:
        verbose_name = 'response block'


class Question(models.Model):
    response_block = models.ForeignKey(ResponseBlock, on_delete=models.CASCADE)
    text = models.TextField(help_text='The text of this question.')
    max_attempts = models.PositiveIntegerField(default=0, help_text='The maximum number of attempts a student has at '
                                                                    'this question. If a value other than 0 is '
                                                                    'provided, then this value overrides the value set '
                                                                    'on the response block.')
    max_points = models.PositiveIntegerField(default=0, help_text='The maximum number of points that can be earned for '
                                                                  'this question. If a value other than 0 is provided, '
                                                                  'then this value overrides the value set on the '
                                                                  'response block.')

    def __str__(self):
        return self.text

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class MultipleChoiceQuestion(Question):
    correct_response = models.CharField(max_length=1, default='A', choices=MCQ_RESPONSES,
                                        help_text='Correlates to one of the responses above.')

    class Meta:
        verbose_name = 'multiple choice question'


class MultipleChoiceQuestionResponse(models.Model):
    identifier = models.CharField(max_length=1)
    response = models.TextField()
    multiple_choice_question = models.ForeignKey(MultipleChoiceQuestion, on_delete=models.CASCADE)


class TrueFalseQuestion(Question):
    correct_response = models.BooleanField(default=True, choices=((True, 'True'), (False, 'False')),
                                           help_text='The correct response for this question.')

    class Meta:
        verbose_name = 'true/false question'


class Bond(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, help_text='The block to link to this segment.')
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE)
    # The order of the blocks within each segment.
    order = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['block', 'segment'], name='unique_editor_bond_constraint'
            )
        ]
        ordering = ('owner', 'order',)

    def __str__(self):
        return str(self.segment) + ' | ' + str(self.block)

    @classmethod
    def delete_warning(cls):
        return 'Note: any associated blocks will be unlinked and available from within the Content Library.'

    @classmethod
    def filterable(cls):
        return False


class Addendum(models.Model):
    master_syllabus = models.ForeignKey(MasterSyllabus, on_delete=models.CASCADE)
    old_block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='old_block')
    new_block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='new_block')
    date_time = models.DateTimeField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['master_syllabus', 'new_block', 'owner'], name='unique_addendum_constraint'
            )
        ]


class Override(models.Model):
    assignment = models.ForeignKey(ScheduleTopic, models.CASCADE,
                                   help_text='The assignment to be overridden. Only one override can be input per '
                                             'assignment.')
    due_date = models.DateField(help_text='The new due date for this assignment.')
    due_time = models.TimeField(default=datetime.time(23, 59, 0), help_text='The new due time for this assignment.')
    section = models.ForeignKey(Section, models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.assignment.assignment_name + ' (' + self.due_date.strftime('%m/%d/%Y') + ')'

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False

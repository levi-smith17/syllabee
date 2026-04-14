from django.contrib.auth.models import User
from django.db import models
from editor.models import Course, LOGICAL_OPERATORS


class ProgramType(models.Model):
    name = models.CharField(max_length=60, help_text='The name of this program type.')
    abbreviation = models.CharField(max_length=30, blank=True, null=True,
                                    help_text='An abbreviated name for this program type.')

    class Meta:
        ordering = ('name',)
        verbose_name = 'program type'
        verbose_name_plural = 'program types'

    def __str__(self):
        return self.name

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class Program(models.Model):
    name = models.CharField(max_length=60, help_text='The name of this program (e.g., Computer Information Systems).')
    option_name = models.CharField(max_length=60, help_text='The name of this program option (e.g., Business Systems).')
    type = models.ForeignKey(ProgramType, on_delete=models.PROTECT, help_text='The type of this program.')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('type', 'name', 'option_name',)

    def __str__(self):
        return self.option_name + ((', ' + str(self.type.abbreviation)) if self.type.abbreviation else '')

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class ProgramCreditType(models.Model):
    name = models.CharField(max_length=60, help_text='A descriptive name of this credit type.')

    def __str__(self):
        return self.name

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class ProgramTermPeriod(models.Model):
    name = models.CharField(max_length=100, help_text='The name of this term period.')

    class Meta:
        ordering = ('name',)
        verbose_name = 'term period'
        verbose_name_plural = 'term periods'

    def __str__(self):
        return self.name

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class ProgramTermYear(models.Model):
    nominal = models.PositiveIntegerField(default=0, help_text='The academic year as a nominal number (e.g., 1, 2, '
                                                               'etc.).')
    ordinal = models.CharField(max_length=200, help_text='The academic year as an ordinal number (e.g., First, '
                                                         'Second, etc.). Additional text can be added to this field.')

    class Meta:
        ordering = ('nominal',)
        verbose_name = 'term year'
        verbose_name_plural = 'term years'

    def __str__(self):
        return self.ordinal

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class ProgramTerm(models.Model):
    year = models.ForeignKey(ProgramTermYear, on_delete=models.CASCADE, help_text='The academic year this term should '
                                                                                  'belong to.')
    period = models.ForeignKey(ProgramTermPeriod, on_delete=models.CASCADE, help_text='The period of this term.')
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

    class Meta:
        ordering = ('year', 'period',)
        verbose_name = 'term'
        verbose_name_plural = 'terms'

    def __str__(self):
        return str(self.period) + ' (' + str(self.year) + ')'

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class ProgramCourse(models.Model):
    term = models.ForeignKey(ProgramTerm, on_delete=models.PROTECT, help_text='The term within a program that this '
                                                                              'course belongs to.')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, help_text='The internal course.')
    credit_hour_type = models.ForeignKey(ProgramCreditType, on_delete=models.PROTECT,
                                         help_text='The type of credit hours for this course within a program.')
    footnote = models.TextField(blank=True, null=True, help_text='A footnote that accompanies this course.')

    class Meta:
        ordering = ('course__prefix', 'course__number',)
        verbose_name = 'course'
        verbose_name_plural = 'courses'

    def __str__(self):
        return str(self.course)

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class ProgramCourseExtension(ProgramCourse):
    related_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='related_course')
    operator = models.CharField(max_length=3, choices=LOGICAL_OPERATORS,
                                help_text='The logical operator used between this course and the previous course.')

    class Meta:
        ordering = ('course__prefix', 'course__number',)
        verbose_name = 'course'
        verbose_name_plural = 'courses'

    def __str__(self):
        return str(self.course)

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False

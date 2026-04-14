from datetime import time
from django.contrib.auth.models import User
from django.db import models
from editor.models import Section


TIMES = (
    (time(0, 0, 0), '12:00 am'),
    (time(0, 15, 0), '12:15 am'),
    (time(0, 30, 0), '12:30 am'),
    (time(0, 45, 0), '12:45 am'),
    (time(1, 0, 0), '1:00 am'),
    (time(1, 15, 0), '1:15 am'),
    (time(1, 30, 0), '1:30 am'),
    (time(1, 45, 0), '1:45 am'),
    (time(2, 0, 0), '2:00 am'),
    (time(2, 15, 0), '2:15 am'),
    (time(2, 30, 0), '2:30 am'),
    (time(2, 45, 0), '2:45 am'),
    (time(3, 0, 0), '3:00 am'),
    (time(3, 15, 0), '3:15 am'),
    (time(3, 30, 0), '3:30 am'),
    (time(3, 45, 0), '3:45 am'),
    (time(4, 0, 0), '4:00 am'),
    (time(4, 15, 0), '4:15 am'),
    (time(4, 30, 0), '4:30 am'),
    (time(4, 45, 0), '4:45 am'),
    (time(5, 0, 0), '5:00 am'),
    (time(5, 15, 0), '5:15 am'),
    (time(5, 30, 0), '5:30 am'),
    (time(5, 45, 0), '5:45 am'),
    (time(6, 0, 0), '6:00 am'),
    (time(6, 15, 0), '6:15 am'),
    (time(6, 30, 0), '6:30 am'),
    (time(6, 45, 0), '6:45 am'),
    (time(7, 0, 0), '7:00 am'),
    (time(7, 15, 0), '7:15 am'),
    (time(7, 30, 0), '7:30 am'),
    (time(7, 45, 0), '7:45 am'),
    (time(8, 0, 0), '8:00 am'),
    (time(8, 15, 0), '8:15 am'),
    (time(8, 30, 0), '8:30 am'),
    (time(8, 45, 0), '8:45 am'),
    (time(9, 0, 0), '9:00 am'),
    (time(9, 15, 0), '9:15 am'),
    (time(9, 30, 0), '9:30 am'),
    (time(9, 45, 0), '9:45 am'),
    (time(10, 0, 0), '10:00 am'),
    (time(10, 15, 0), '10:15 am'),
    (time(10, 30, 0), '10:30 am'),
    (time(10, 45, 0), '10:45 am'),
    (time(11, 0, 0), '11:00 am'),
    (time(11, 15, 0), '11:15 am'),
    (time(11, 30, 0), '11:30 am'),
    (time(11, 45, 0), '11:45 am'),
    (time(12, 0, 0), '12:00 pm'),
    (time(12, 15, 0), '12:15 pm'),
    (time(12, 30, 0), '12:30 pm'),
    (time(12, 45, 0), '12:45 pm'),
    (time(13, 0, 0), '1:00 pm'),
    (time(13, 15, 0), '1:15 pm'),
    (time(13, 30, 0), '1:30 pm'),
    (time(13, 45, 0), '1:45 pm'),
    (time(14, 0, 0), '2:00 pm'),
    (time(14, 15, 0), '2:15 pm'),
    (time(14, 30, 0), '2:30 pm'),
    (time(14, 45, 0), '2:45 pm'),
    (time(15, 0, 0), '3:00 pm'),
    (time(15, 15, 0), '3:15 pm'),
    (time(15, 30, 0), '3:30 pm'),
    (time(15, 45, 0), '3:45 pm'),
    (time(16, 0, 0), '4:00 pm'),
    (time(16, 15, 0), '4:15 pm'),
    (time(16, 30, 0), '4:30 pm'),
    (time(16, 45, 0), '4:45 pm'),
    (time(17, 0, 0), '5:00 pm'),
    (time(17, 15, 0), '5:15 pm'),
    (time(17, 30, 0), '5:30 pm'),
    (time(17, 45, 0), '5:45 pm'),
    (time(18, 0, 0), '6:00 pm'),
    (time(18, 15, 0), '6:15 pm'),
    (time(18, 30, 0), '6:30 pm'),
    (time(18, 45, 0), '6:45 pm'),
    (time(19, 0, 0), '7:00 pm'),
    (time(19, 15, 0), '7:15 pm'),
    (time(19, 30, 0), '7:30 pm'),
    (time(19, 45, 0), '7:45 pm'),
    (time(20, 0, 0), '8:00 pm'),
    (time(20, 15, 0), '8:15 pm'),
    (time(20, 30, 0), '8:30 pm'),
    (time(20, 45, 0), '8:45 pm'),
    (time(21, 0, 0), '9:00 pm'),
    (time(21, 15, 0), '9:15 pm'),
    (time(21, 30, 0), '9:30 pm'),
    (time(21, 45, 0), '9:45 pm'),
    (time(22, 0, 0), '10:00 pm'),
    (time(22, 15, 0), '10:15 pm'),
    (time(22, 30, 0), '10:30 pm'),
    (time(22, 45, 0), '10:45 pm'),
    (time(23, 0, 0), '11:00 pm'),
    (time(23, 15, 0), '11:15 pm'),
    (time(23, 30, 0), '11:30 pm'),
    (time(23, 45, 0), '11:45 pm'),
)


class Internship(models.Model):
    section = models.ForeignKey(Section, on_delete=models.PROTECT, help_text='Section associated with this internship.')
    intern = models.ForeignKey(User, unique=True, on_delete=models.PROTECT,
                               help_text='Intern associated with this internship.')
    completed_hours = models.FloatField(default=0, help_text='The number or hours completed for this internship.')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['section', 'intern'], name='unique_section_intern_constraint'
            )
        ]
        ordering = ('-section__term__term_code', 'section__course__prefix', 'section__course__number',
                    'section__section_code', 'intern__last_name', 'intern__first_name')
        verbose_name = 'internship'
        verbose_name_plural = 'internships'

    def __str__(self):
        return str(self.section) + ' - ' + str(self.intern)

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class InternshipLocation(models.Model):
    internship = models.ForeignKey(Internship, on_delete=models.PROTECT)
    name = models.CharField(max_length=255,
                            help_text='The name of the business where the internship is located.')
    address_1 = models.CharField(max_length=255,
                                 help_text='The first line of the business address where the internship '
                                           'is located.')
    address_2 = models.CharField(max_length=255, blank=True, null=True,
                                 help_text='The second line of the business address.')
    city = models.CharField(max_length=255, help_text='The city associated with the business.')
    state = models.CharField(max_length=30, help_text='The state associated with the business.')
    zip = models.CharField(max_length=5,
                           help_text='The zip code associated with the business (five digits only).')
    supervisor_first_name = models.CharField(max_length=64, help_text='The supervisor\'s first name.')
    supervisor_last_name = models.CharField(max_length=64, help_text='The supervisor\'s last name.')
    supervisor_email = models.CharField(max_length=255, help_text='The supervisor\'s email address.')
    supervisor_phone = models.CharField(max_length=10, blank=True, null=True,
                                        help_text='The supervisor\'s phone number (digits only).')
    validated = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, help_text='The date and time this location was created.')

    class Meta:
        ordering = ('internship', 'name',)
        verbose_name = 'internship location'
        verbose_name_plural = 'internship locations'

    def __str__(self):
        return str(self.name)

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class InternshipJournalEntry(models.Model):
    location = models.ForeignKey(InternshipLocation, on_delete=models.CASCADE,
                                 help_text='Location of the internship where the activity for this journal entry '
                                           'took place.')
    title = models.CharField(max_length=255, help_text='A generic title for this journal entry (e.g., Set Up '
                                                       'Computers, Manned the Help Desk, or Met with Supervisor, '
                                                       'etc.).')
    description = models.TextField(help_text='Details of the activities for this journal entry. Please describe what '
                                             'you did during this time and be as thorough as possible.')
    date = models.DateField(help_text='Date of this journal entry.')
    time_start = models.TimeField(choices=TIMES, help_text='Time the activity started for this journal entry (rounded '
                                                           'to the nearest 15 minutes).')
    time_end = models.TimeField(choices=TIMES, help_text='Time the activity ended for this journal entry (rounded to '
                                                         'the nearest 15 minutes)')
    total_time_minutes = models.IntegerField(help_text='Additional time for this activity (in minutes) beyond provided '
                                                       'hours (e.g., if you completed an activity that took 2 hours '
                                                       'and 45 minutes, then input 2 in the input box above and 45 '
                                                       'minutes in this input box).')
    verified = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, help_text='The date and time this journal entry was created.')

    class Meta:
        ordering = ('-date', 'time_start',)
        verbose_name = 'journal entry'
        verbose_name_plural = 'journal entries'

    def __str__(self):
        return 'Journal Entry (' + str(self.date) + ') - ' + str(self.title)

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class InternshipSettings(models.Model):
    coordinator = models.ForeignKey(User, on_delete=models.PROTECT, unique=True)
    journal_points = models.FloatField(default=400, help_text='The total number of points awarded for an internship '
                                                              'journal.')
    journal_required_hours = models.FloatField(default=224, help_text='The number of hours needed to complete '
                                                                      'an internship.')

    class Meta:
        verbose_name = 'internship setting'
        verbose_name_plural = 'internship settings'

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False

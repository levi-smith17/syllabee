from ..models import InternshipLocation, InternshipJournalEntry
from core.widgets import QuillWidget
from datetime import datetime, time
from django import forms
from django.core.exceptions import ValidationError


class InternshipJournalEntryForm(forms.ModelForm):
    location = forms.CharField(widget=forms.HiddenInput(), required=False)
    description = forms.CharField(widget=None, help_text=InternshipJournalEntry._meta.get_field('description').help_text)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}),
                           help_text=InternshipJournalEntry._meta.get_field('date').help_text)
    total_time_minutes = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.location_id = kwargs.pop('location_id')
        super(InternshipJournalEntryForm, self).__init__(*args, **kwargs)
        self.fields['location'].initial = self.location_id
        self.fields['description'].widget = QuillWidget(attrs={'disabled': False, 'required': True})
        self.fields['total_time_minutes'].initial = 0

    class Meta:
        model = InternshipJournalEntry
        exclude = ('verified', 'timestamp',)

    def clean_location(self):
        try:
            return InternshipLocation.objects.get(pk=self.cleaned_data['location'])
        except InternshipLocation.DoesNotExist:
            raise ValidationError('The requested location does not exist.')

    def clean_total_time_minutes(self):
        date = self.cleaned_data['date']
        time_start = datetime.combine(date, self.cleaned_data['time_start'])
        time_end = datetime.combine(date, self.cleaned_data['time_end'])
        time_difference = time_end - time_start
        return time_difference.total_seconds() / 60

    def clean(self):
        if self.cleaned_data['time_start'] >= self.cleaned_data['time_end']:
            raise ValidationError('The end time cannot be before (or the same as) the start time.')
        entries = (InternshipJournalEntry.objects
                    .filter(date=self.cleaned_data['date'], location_id=self.cleaned_data['location'])
                    .exclude(pk=self.instance.pk))
        for entry in entries:
            if (entry.time_start < self.cleaned_data['time_start'] < entry.time_end or
                    entry.time_start < self.cleaned_data['time_end'] < entry.time_end):
                raise ValidationError('The provided time conflicts with an existing journal entry. Please review the '
                                      'journal entry times for the provided date. Conflicting entry has time: ' +
                                      str(datetime.strptime(str(entry.time_start), "%H:%M:%S").strftime("%I:%M %p"))
                                      + ' - ' +
                                      str(datetime.strptime(str(entry.time_end), "%H:%M:%S").strftime("%I:%M %p"))
                                      + '.')


class InternshipJournalEntryDeleteForm(forms.ModelForm):
    class Meta:
        model = InternshipJournalEntry
        exclude = ('location', 'title', 'description', 'date', 'time_start', 'time_end', 'total_time_hours',
                   'total_time_minutes', 'verified', 'timestamp',)

from ..models import Internship, Section, User
from core.widgets import DatalistWidget
from django import forms
from django.core.exceptions import ValidationError


class InternshipForm(forms.ModelForm):
    section = forms.ModelChoiceField(queryset=None, help_text=Internship._meta.get_field('section').help_text)
    intern = forms.CharField(widget=None, help_text=Internship._meta.get_field('intern').help_text)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(InternshipForm, self).__init__(*args, **kwargs)
        self.fields['section'].queryset = Section.objects.filter(instructor=self.user, format='Internship',
                                                                 term__archived=False)
        self.fields['intern'].widget = DatalistWidget(model=User)

    class Meta:
        model = Internship
        fields = '__all__'

    def clean_intern(self):
        try:
            name = self.cleaned_data['intern'].split(', ')
            return User.objects.get(last_name=name[0], first_name=name[1])
        except User.DoesNotExist:
            raise ValidationError('The requested intern does not exist.')


class InternshipDeleteForm(forms.ModelForm):

    class Meta:
        model = Internship
        exclude = ('section', 'intern', 'completed_hours', 'required_hours',)

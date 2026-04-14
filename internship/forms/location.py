from ..models import Internship, InternshipLocation
from django import forms
from django.core.exceptions import ValidationError


class InternshipLocationForm(forms.ModelForm):
    internship = forms.CharField(widget=forms.HiddenInput(), required=False)
    supervisor_email = forms.EmailField(help_text=InternshipLocation._meta.get_field('supervisor_email').help_text)

    def __init__(self, *args, **kwargs):
        self.internship_id = kwargs.pop('internship_id')
        super(InternshipLocationForm, self).__init__(*args, **kwargs)
        self.fields['internship'].initial = self.internship_id

    class Meta:
        model = InternshipLocation
        exclude = ('validated', 'timestamp',)

    def clean_internship(self):
        try:
            return Internship.objects.get(pk=self.cleaned_data['internship'])
        except Internship.DoesNotExist:
            raise ValidationError('The requested internship does not exist.')


class InternshipLocationDeleteForm(forms.ModelForm):
    class Meta:
        model = InternshipLocation
        exclude = ('internship', 'name', 'address_1', 'address_2', 'city', 'state', 'zip', 'supervisor_last_name',
                   'supervisor_first_name', 'supervisor_email', 'supervisor_phone', 'validated', 'timestamp')

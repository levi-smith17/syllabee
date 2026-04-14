from ..models import ProgramTerm
from django import forms


class TermForm(forms.ModelForm):
    class Meta:
        model = ProgramTerm
        exclude = ('program',)


class TermDeleteForm(forms.ModelForm):
    class Meta:
        model = ProgramTerm
        exclude = ('year', 'period', 'program',)
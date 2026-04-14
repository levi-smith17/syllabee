from ..models import Program
from django import forms


class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        exclude = ('owner',)


class ProgramDeleteForm(forms.ModelForm):
    class Meta:
        model = Program
        exclude = ('name', 'type', 'owner',)
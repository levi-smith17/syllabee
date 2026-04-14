from ...models import ProgramCourse, ProgramTerm
from core.widgets import DatalistWidget
from django import forms
from django.db.models import Q
from editor.models import Course
from editor.forms.registration.course import clean_course_generic


class CourseCreateForm(forms.ModelForm):
    course = forms.CharField(widget=None, help_text=ProgramCourse._meta.get_field('course').help_text)

    def __init__(self, *args, **kwargs):
        self.program_id = kwargs.pop('program_id')
        super(CourseCreateForm, self).__init__(*args, **kwargs)
        self.fields['course'].widget = DatalistWidget(model=Course, filters=(Q(inactive=False)),
                                                      choices=[(o.course_code + ' - ' + o.name) for o in Course.objects.filter(Q(inactive=False))],
                                                      attrs={'disabled': False, 'required': True})
        self.fields['footnote'].widget.attrs['style'] = 'height: 10rem'

    class Meta:
        model = ProgramCourse
        exclude = ('term',)

    def clean_course(self):
        return clean_course_generic(self)



class CourseDeleteForm(forms.ModelForm):
    class Meta:
        model = ProgramCourse
        exclude = ('course', 'credit_hour_type','footnote', 'term',)


class CourseUpdateForm(forms.ModelForm):
    course = forms.CharField(widget=None, help_text=ProgramCourse._meta.get_field('course').help_text)

    def __init__(self, *args, **kwargs):
        self.program_id = kwargs.pop('program_id')
        super(CourseUpdateForm, self).__init__(*args, **kwargs)
        self.fields['course'].widget = DatalistWidget(model=Course, filters=(Q(inactive=False)),
                                                      choices=[(o.course_code + ' - ' + o.name) for o in Course.objects.filter(Q(inactive=False))],
                                                      attrs={'disabled': False, 'required': True})
        self.fields['footnote'].widget.attrs['style'] = 'height: 10rem'
        self.fields['term'].queryset = ProgramTerm.objects.filter(program_id=self.program_id)

    class Meta:
        model = ProgramCourse
        fields = '__all__'

    def clean_course(self):
        return clean_course_generic(self)

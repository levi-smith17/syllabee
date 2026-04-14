from ...models import ProgramCourseExtension
from core.widgets import DatalistWidget
from django import forms
from django.db.models import Q
from editor.models import Course
from editor.forms.registration.course import clean_course_generic


class CourseExtensionForm(forms.ModelForm):
    course = forms.CharField(widget=None, help_text=ProgramCourseExtension._meta.get_field('course').help_text)

    def __init__(self, *args, **kwargs):
        super(CourseExtensionForm, self).__init__(*args, **kwargs)
        self.fields['course'].widget = DatalistWidget(model=Course, filters=(Q(inactive=False)),
                                                      choices=[(o.course_code + ' - ' + o.name) for o in Course.objects.filter(Q(inactive=False))],
                                                      attrs={'disabled': False, 'required': True})
        self.fields['footnote'].widget.attrs['style'] = 'height: 10rem'

    class Meta:
        model = ProgramCourseExtension
        exclude = ('related_course', 'term',)

    def clean_course(self):
        return clean_course_generic(self)



class CourseExtensionDeleteForm(forms.ModelForm):
    class Meta:
        model = ProgramCourseExtension
        exclude = ('course', 'credit_hour_type', 'footnote', 'operator', 'related_course', 'term')

from core.views.mixins import FormInvalidMixin
from django.views.generic import CreateView, UpdateView
from editor.views.block import BlockCreateMixin, BlockUpdateMixin
from editor.forms.blocks.course_syllabus import *


class CourseSyllabusBlockCreateView(BlockCreateMixin, FormInvalidMixin, CreateView):
    model = CourseSyllabusBlock
    form_class = CourseSyllabusBlockForm


class CourseSyllabusBlockUpdateView(BlockUpdateMixin, FormInvalidMixin, UpdateView):
    model = CourseSyllabusBlock
    form_class = CourseSyllabusBlockForm

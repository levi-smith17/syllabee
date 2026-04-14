from core.views.mixins import FormInvalidMixin
from django.views.generic import CreateView, UpdateView
from editor.forms.blocks.grade_determination import *
from editor.views.block import BlockCreateMixin, BlockUpdateMixin
from editor.views.mixins import SectionRequiredAccessMixin


class GradeDeterminationBlockCreateView(SectionRequiredAccessMixin, BlockCreateMixin, FormInvalidMixin, CreateView):
    model = GradeDeterminationBlock
    form_class = GradeDeterminationBlockForm


class GradeDeterminationBlockUpdateView(BlockUpdateMixin, FormInvalidMixin, UpdateView):
    model = GradeDeterminationBlock
    form_class = GradeDeterminationBlockForm

from core.views.mixins import FormInvalidMixin
from django.views.generic import CreateView, UpdateView
from editor.views.block import BlockCreateMixin, BlockUpdateMixin
from editor.forms.blocks.details import *


class DetailsBlockCreateView(BlockCreateMixin, FormInvalidMixin, CreateView):
    model = DetailsBlock
    form_class = DetailsBlockForm


class DetailsBlockUpdateView(BlockUpdateMixin, FormInvalidMixin, UpdateView):
    model = DetailsBlock
    form_class = DetailsBlockForm

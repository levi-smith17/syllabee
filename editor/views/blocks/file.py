from core.views.mixins import FormInvalidMixin
from django.views.generic import CreateView, UpdateView
from editor.views.block import BlockCreateMixin, BlockUpdateMixin
from editor.forms.blocks.file import *


class FileBlockCreateView(BlockCreateMixin, FormInvalidMixin, CreateView):
    model = FileBlock
    form_class = FileBlockForm


class FileBlockUpdateView(BlockUpdateMixin, FormInvalidMixin, UpdateView):
    model = FileBlock
    form_class = FileBlockForm

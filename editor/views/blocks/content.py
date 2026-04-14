from core.views.mixins import FormInvalidMixin
from django.views.generic import CreateView, UpdateView
from editor.views.block import BlockCreateMixin, BlockUpdateMixin
from editor.forms.blocks.content import *


class ContentBlockCreateView(BlockCreateMixin, FormInvalidMixin, CreateView):
    model = ContentBlock
    form_class = ContentBlockCreateForm


class ContentBlockUpdateView(BlockUpdateMixin, FormInvalidMixin, UpdateView):
    model = ContentBlock
    form_class = ContentBlockUpdateForm

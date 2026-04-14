from core.views.mixins import FormInvalidMixin
from django.views.generic import CreateView, UpdateView
from editor.views.block import BlockCreateMixin, BlockUpdateMixin
from editor.forms.blocks.video import *


class VideoBlockCreateView(BlockCreateMixin, FormInvalidMixin, CreateView):
    model = VideoBlock
    form_class = VideoBlockForm


class VideoBlockUpdateView(BlockUpdateMixin, FormInvalidMixin, UpdateView):
    model = VideoBlock
    form_class = VideoBlockForm

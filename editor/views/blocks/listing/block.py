from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import FormInvalidMixin
from django.urls import reverse
from django.views.generic import CreateView, UpdateView
from editor.views.block import BlockCreateMixin,  BlockUpdateMixin
from editor.forms.blocks.list_block import *


class ListBlockCreateView(BlockCreateMixin, FormInvalidMixin, CreateView):
    model = ListBlock
    form_class = ListBlockForm


class ListBlockUpdateView(BlockUpdateMixin, FormInvalidMixin, UpdateView):
    model = ListBlock
    form_class = ListBlockForm


class ListBlockPropertiesUpdateView(BlockUpdateMixin, FormInvalidMixin, UpdateView):
    model = ListBlock
    form_class = ListBlockPropertiesForm

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = False
        context['edit_url'] = reverse('editor:block:list:update_properties',
                                      args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                            self.object.id,))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}

    def get_success_url(self):
        return reverse('editor:block:list:update', args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                        self.kwargs['pk'],))

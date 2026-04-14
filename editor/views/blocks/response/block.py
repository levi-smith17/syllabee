from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView, View
from django.views.generic.base import ContextMixin
from editor.views.block import BlockCreateMixin, BlockUpdateMixin
from editor.forms.blocks.response import *


class QuestionContextMixin(ContextMixin, View):
    def get_success_url(self):
        return reverse('editor:block:response:list', args=(self.kwargs['master_syllabus_id'],
                                                          self.kwargs['segment_id'], self.kwargs['block_id'],))


class ResponseBlockCreateView(BlockCreateMixin, FormInvalidMixin, CreateView):
    model = ResponseBlock
    form_class = ResponseBlockForm


class ResponseBlockListView(PermissionRequiredMixin, ListView):
    permission_required = ('editor.view_mastersyllabus',)
    model = ResponseBlock
    template_name = 'editor/mastersyllabus/segment/block/card/response/list.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['bond'] = Bond.objects.get(segment_id=self.kwargs['segment_id'], block_id=self.kwargs['pk'])
        context['master_syllabus'] = MasterSyllabus.objects.get(pk=self.kwargs['master_syllabus_id'])
        context['questions'] = Question.objects.filter(response_block=self.kwargs['pk'])
        return {**context, **environs}


class ResponseBlockUpdateView(BlockUpdateMixin, FormInvalidMixin, UpdateView):
    model = ResponseBlock
    form_class = ResponseBlockForm

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['callback'] = 'done_close_full'
        context['questions'] = Question.objects.filter(response_block=self.kwargs['pk'])
        return {**context, **environs}


class ResponseBlockPropertiesUpdateView(BlockUpdateMixin, FormInvalidMixin, UpdateView):
    permission_required = 'editor.change_responseblock'
    model = ResponseBlock
    form_class = ResponseBlockPropertiesForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = False
        context['edit_url'] = reverse('editor:block:response:update_properties',
                                      args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                            self.object.id,))
        context['target'] = '.offcanvas-full-container'
        return {**context, **environs}

    def get_success_url(self):
        return reverse('editor:block:response:update', args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                            self.kwargs['pk'],))


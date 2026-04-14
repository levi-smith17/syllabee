from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView
from editor.forms.blocks.true_false_question import *
from editor.views.blocks.response import QuestionContextMixin


class TrueFalseQuestionCreateView(PermissionRequiredMixin, FormInvalidMixin, QuestionContextMixin, CreateView):
    permission_required = ('editor.add_true_false_question',)
    model = TrueFalseQuestion
    form_class = TrueFalseQuestionForm
    template_name = 'core/offcanvas/add.html'

    def form_valid(self, form):
        form.instance.response_block = ResponseBlock.objects.get(pk=self.kwargs['block_id'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:block:response:true_false_question:create',
                                     args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                           self.kwargs['block_id'],))
        context['callback'] = 'done_generic'
        context['render_mode'] = 'edit'
        context['target'] = '#question-container'
        return {**context, **environs}


class TrueFalseQuestionDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin, QuestionContextMixin,
                         DeleteView):
    permission_required = ('editor.delete_true_false_question',)
    model = TrueFalseQuestion
    form_class = TrueFalseQuestionDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['callback'] = 'done_generic'
        context['modal']['target'] = '#question-container'
        context['modal']['url'] = reverse('editor:block:response:true_false_question:delete',
                                          args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                self.kwargs['block_id'], self.object.id,))
        return context


class TrueFalseQuestionUpdateView(PermissionRequiredMixin, FormInvalidMixin, QuestionContextMixin, UpdateView):
    permission_required = ('editor.change_true_false_question',)
    model = TrueFalseQuestion
    form_class = TrueFalseQuestionForm
    template_name = 'core/offcanvas/edit.html'


    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['callback'] = 'done_generic'
        context['delete_url'] = None
        context['edit_url'] = reverse('editor:block:response:true_false_question:update',
                                      args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                            self.kwargs['block_id'], self.kwargs['pk'],))
        context['target'] = '#question-container'
        return {**context, **environs}

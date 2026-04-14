from core.views import get_environs, get_cbv_context
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView
from editor.forms.blocks.multiple_choice_question import *
from editor.views.blocks.response import QuestionContextMixin


class MultipleChoiceQuestionCreateView(PermissionRequiredMixin, FormInvalidMixin, QuestionContextMixin, CreateView):
    permission_required = ('editor.add_multiple_choice_question',)
    model = MultipleChoiceQuestion
    form_class = MultipleChoiceQuestionForm
    template_name = 'editor/mastersyllabus/segment/block/card/response/add.html'

    def form_valid(self, form):
        form.instance.response_block = ResponseBlock.objects.get(pk=self.kwargs['block_id'])
        self.object = form.save()
        formsets = ResponseFormSet(self.request.POST)
        for formset in formsets:
            if formset.is_valid():
                formset.instance.multiple_choice_question_id = self.object.id
                formset.save()
            else:
                return super().form_invalid(formset)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:block:response:multiple_choice_question:create',
                                     args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                           self.kwargs['block_id'],))
        context['callback'] = 'done_generic'
        context['formset'] = ResponseFormSet()
        context['render_mode'] = 'edit'
        context['target'] = '#question-container'
        return {**context, **environs}


class MultipleChoiceQuestionDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin,
                                       QuestionContextMixin, DeleteView):
    permission_required = 'editor.delete_multiple_choice_question'
    model = MultipleChoiceQuestion
    form_class = MultipleChoiceQuestionDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['callback'] = 'done_generic'
        context['modal']['target'] = '#question-container'
        context['modal']['url'] = reverse('editor:block:response:multiple_choice_question:delete',
                                          args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                                self.kwargs['block_id'], self.object.id,))
        return context


class MultipleChoiceQuestionUpdateView(PermissionRequiredMixin, FormInvalidMixin, QuestionContextMixin, UpdateView):
    permission_required = ('editor.change_multiple_choice_question',)
    model = MultipleChoiceQuestion
    form_class = MultipleChoiceQuestionForm
    template_name = 'editor/mastersyllabus/segment/block/card/response/edit.html'

    def form_valid(self, form):
        self.object = form.save()
        formsets = ResponseFormSet(self.request.POST, instance=self.object)
        for formset in formsets:
            if formset.is_valid():
                formset.instance.multiple_choice_question_id = self.object.id
                formset.save()
            else:
                return super().form_invalid(formset)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['callback'] = 'done_generic'
        context['delete_url'] = None
        context['edit_url'] = reverse('editor:block:response:multiple_choice_question:update',
                                      args=(self.kwargs['master_syllabus_id'], self.kwargs['segment_id'],
                                            self.kwargs['block_id'], self.kwargs['pk'],))
        context['formset'] = ResponseFormSet(instance=self.object)
        context['target'] = '#question-container'
        return {**context, **environs}

from ..forms import *
from core.views.funcs import get_cbv_context, get_environs, handler_form
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import IntegrityError
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.views.generic.edit import FormMixin


class GradingScaleFormMixin(FormMixin):
    def post(self, *args, **kwargs):
        if 'pk' in self.kwargs:  # We're editing a grading scale.
            grade_scale = GradingScale.objects.get(pk=self.kwargs['pk'])
            grading_scale_form = GradingScaleForm(self.request.POST, instance=grade_scale)
        else:  # We're adding a grading scale.
            grading_scale_form = GradingScaleForm(self.request.POST)
        if grading_scale_form.is_valid():
            if 'pk' not in self.kwargs:
                grading_scale_form.instance.owner = self.request.user
            grade_scale = grading_scale_form.save()
            formset = GradeFormSet(self.request.POST, self.request.FILES, instance=grade_scale)
            if formset.is_valid():
                try:
                    formset.save()
                except IntegrityError:
                    return handler_form(self.request,
                                        exceptions={'exceptions': {'Grade letters can only be added once to each '
                                                                   'grading scale. Please ensure that each grade '
                                                                   'letter is unique.'}})
                return super().form_valid(grading_scale_form)
            else:
                return handler_form(self.request,
                                    exceptions={'exceptions': {'Your inputs are invalid. Please make sure that all '
                                                               'fields have a value and at least one grade letter '
                                                               'row exists (and has been completed).'}})
        return super().form_invalid(grading_scale_form)


class GradingScaleCreateView(PermissionRequiredMixin, FormInvalidMixin, GradingScaleFormMixin, CreateView):
    permission_required = ('editor.add_gradingscale',)
    model = GradingScale
    form_class = GradingScaleForm
    template_name = 'core/offcanvas/add.html'
    success_url = reverse_lazy('editor:gradingscale:list')

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('editor:gradingscale:create')
        context['callback'] = 'done_close_full'
        context['formset'] = GradeFormSet()
        context['target'] = '#grading-scales-container'
        return {**context, **environs}

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class GradingScaleDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin, DeleteView):
    permission_required = ('editor.delete_gradingscale',)
    model = GradingScale
    form_class = GradingScaleDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['callback'] = 'done_close_full'
        context['modal']['target'] = '#grading-scales-container'
        context['modal']['url'] = reverse('editor:gradingscale:delete', args=(self.object.id,))
        return context

    def get_success_url(self):
        return reverse('editor:gradingscale:list')


class GradingScaleListView(PermissionRequiredMixin, ListView):
    permission_required = ('editor.view_gradingscale',)
    model = GradingScale
    template_name = 'editor/gradingscale/list.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['grading_scales'] = GradingScale.objects.filter(owner=self.request.user)
        return {**context, **environs}


class GradingScaleUpdateView(PermissionRequiredMixin, FormInvalidMixin, GradingScaleFormMixin, UpdateView):
    permission_required = ('editor.change_gradingscale', 'editor.delete_gradingscale',)
    model = GradingScale
    form_class = GradingScaleForm
    template_name = 'core/offcanvas/edit.html'
    success_url = reverse_lazy('editor:gradingscale:list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['callback'] = 'done_close_full'
        context['delete_url'] = reverse('editor:gradingscale:delete', args=(self.object.id,))
        context['edit_url'] = reverse('editor:gradingscale:update', args=(self.object.id,))
        context['formset'] = GradeFormSet(instance=self.object)
        context['target'] = '#grading-scales-container'
        return {**context, **environs}

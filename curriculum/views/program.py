from ..forms import ProgramForm, ProgramDeleteForm
from ..models import Program, ProgramCourse, ProgramCourseExtension, ProgramCreditType, ProgramTerm
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from datetime import datetime
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View
from django.views.generic.base import ContextMixin


class ProgramContextMixin(ContextMixin, View):
    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super(ProgramContextMixin, self).get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['program_id'] = -1
        context['program'] = None
        try:
            program = self.request.session.get('program_id', None)
            if 'pk' in self.kwargs:
                context['program_id'] = self.kwargs['pk']
            elif program:
                context['program_id'] = program
            else:
                context['program_id'] = Program.objects.filter(owner=self.request.user).first().id
            context['courses'] = (ProgramCourse.objects
                                  .filter(term__program_id=context['program_id'])
                                  .exclude(pk__in=ProgramCourseExtension.objects.all())
                                  .order_by('term__year', 'term__period', 'course__prefix', 'course__number'))
            context['credit_types'] = ProgramCreditType.objects.all()
            context['current_date'] = datetime.today().strftime('%d %B %Y')
            context['program'] = Program.objects.get(pk=context['program_id'])
            context['terms'] = ProgramTerm.objects.filter(program__id=context['program_id'])
            context['title'] = str(context['program'])
        except Exception as e:
            context['error'] = e
        self.request.session['program_id'] = context['program_id']
        return {**context, **environs}


class ProgramCreateView(PermissionRequiredMixin, FormInvalidMixin, CreateView):
    permission_required = ('curriculum.add_program',)
    model = Program
    form_class = ProgramForm
    success_url = reverse_lazy('curriculum:program:list')
    template_name = 'core/offcanvas/add.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('curriculum:program:create')
        context['target'] = '#program-list'
        return {**context, **environs}

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ProgramDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin, DeleteView):
    permission_required = ('curriculum.delete_program',)
    model = Program
    form_class = ProgramDeleteForm
    success_url = reverse_lazy('curriculum:program:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal']['target'] = '#program-list'
        context['modal']['url'] = reverse('curriculum:program:delete', args=(self.object.id,))
        return context


class ProgramDetailView(PermissionRequiredMixin, ProgramContextMixin, DetailView):
    permission_required = ('curriculum.view_program',)
    model = Program
    template_name = 'curriculum/program/card/card.html'


class ProgramListView(PermissionRequiredMixin, ProgramContextMixin, ListView):
    permission_required = ('curriculum.view_program',)
    model = Program
    template_name = 'curriculum/program/list.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['programs'] = Program.objects.filter(owner=self.request.user)
        return {**context, **environs}


class ProgramPrintView(PermissionRequiredMixin, ProgramContextMixin, DetailView):
    permission_required = ('curriculum.view_program',)
    model = Program
    template_name = 'curriculum/print/index.html'


class ProgramUpdateView(PermissionRequiredMixin, FormInvalidMixin, UpdateView):
    permission_required = ('curriculum.change_program', 'curriculum.delete_program',)
    model = Program
    form_class = ProgramForm
    success_url = reverse_lazy('curriculum:program:list')
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['delete_url'] = None
        context['edit_url'] = reverse('curriculum:program:update', args=(self.object.id,))
        context['target'] = '#program-list'
        return {**context, **environs}

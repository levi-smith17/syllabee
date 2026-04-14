from core.views.funcs import get_environs
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView, DetailView
from editor.models import MasterBond, MasterBondSection, MasterSyllabus, Section, Question
from viewer.models import AttemptProgress, BondProgress, MasterBondProgress, ResponseProgress, SectionProgress
from django.urls import reverse
from viewer.views.mixins import ProgressResetMixin


class ProgressDashboardView(PermissionRequiredMixin, TemplateView):
    permission_required = ('viewer.view_sectionprogress',)
    template_name = 'editor/progress/dashboard.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['master_syllabus'] = MasterSyllabus.objects.get(pk=self.kwargs['master_syllabus_id'])
        context['master_bond_sections'] = (MasterBondSection.objects
                                           .filter(master_bond__master_syllabus=context['master_syllabus']))
        context['section'] = None
        return {**context, **environs}


class ProgressDetailView(PermissionRequiredMixin, DetailView):
    permission_required = ('viewer.view_sectionprogress',)
    model = Section
    template_name = 'editor/progress/card/card.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['master_syllabus'] = MasterSyllabus.objects.get(pk=self.kwargs['master_syllabus_id'])
        context['master_bond'] = MasterBond.objects.get(masterbondsection__section=self.object)
        context['master_bond_sections'] = (MasterBondSection.objects
                                           .filter(master_bond__master_syllabus=context['master_syllabus']))
        context['section_progresses'] = (SectionProgress.objects
                                         .filter(section=self.object)
                                         .order_by('student__last_name', 'student__first_name'))
        return {**context, **environs}


class ProgressResetView(ProgressResetMixin):
    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['callback'] = 'done_generic'
        context['content_id'] = ''
        context['modal']['target'] = '#content-container'
        context['modal']['url'] = reverse('editor:mastersyllabus:progress:reset',
                                          args=(self.kwargs['master_syllabus_id'], self.kwargs['section_hash'],
                                                self.kwargs['student_id'],))
        return {**context, **environs}

    def get_success_url(self):
        section = Section.objects.get(hash=self.kwargs['section_hash'])
        return reverse('editor:mastersyllabus:progress:detail', args=(self.kwargs['master_syllabus_id'],
                                                                     section.id,))


class ProgressStudentDetailView(PermissionRequiredMixin, TemplateView):
    permission_required = ('viewer.view_sectionprogress',)
    template_name = 'editor/progress/card/details/details.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        section_progress = SectionProgress.objects.get(pk=self.kwargs['section_progress_id'])
        master_bond_progresses = (MasterBondProgress.objects
                                  .filter(section_progress=section_progress)
                                  .order_by('master_bond__order'))
        bond_progresses = (BondProgress.objects
                           .filter(master_bond_progress__section_progress=section_progress)
                           .order_by('bond__order'))
        context.update({'bond_progresses': bond_progresses, 'master_bond_progresses': master_bond_progresses,
                        'master_syllabus': section_progress.master_syllabus, 'section_progress': section_progress})
        return {**context, **environs}


class ProgressAttemptDetailView(PermissionRequiredMixin, TemplateView):
    permission_required = ('viewer.view_attemptprogress',)
    template_name = 'editor/progress/card/details/attempts_detail.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        attempts = (AttemptProgress.objects
                    .filter(response_progress=self.kwargs['response_progress_id'])
                    .order_by('count'))
        master_syllabus = MasterSyllabus.objects.get(pk=self.kwargs['master_syllabus_id'])
        question = Question.objects.get(responseprogress__id=self.kwargs['response_progress_id'])
        response_progress = ResponseProgress.objects.get(pk=self.kwargs['response_progress_id'])
        context.update({'attempts': attempts, 'master_syllabus': master_syllabus,'question': question,
                        'response_progress': response_progress})
        return {**context, **environs}
